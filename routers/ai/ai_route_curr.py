import enum
import logging
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from Ai.sentiment_analysis import sentiment_analysis_ai
from Ai.title_gen import generate_titles
from Ai.summry_ai import summry_ai
from core.exceptions import AIServiceException
from db import get_db
from Oauth2 import get_user_jwt_payload
from Ai.Ai_rephrase_content import rephraser
from Ai.main import model
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from db_tables.tables import AIUsageTrackerTable 
from routers.ai.ai_helpers import Quota_check
from utils.schemas import AIGatewayContext, AIRequestState, LogContext
from utils.ai_responce_handler import handle_service_response, is_system_failure

from utils.logging.helper_log import log_state, LogState
from utils.logging.logEvents import (
    AuthLog,
    DatabaseLog,
    ExceptionLog,
    ReservationLog,
    GatewayLog
)

from utils.schemas import (
    APIResponse,
    RephraseOutput_route,
    RephraseRequest_route,
    SentimentAnalysisOut_route,
    SentimentAnalysisRequest_route,
    SummaryOut_route,
    SummaryRequest_route,
    Title_genOut_Route,
    Title_genRequest_Route,
    TokenDataSchema
)
from utils.schemas import QuotaStatus


#utils
async def consume_ai_quota(db: AsyncSession, user_id: int, request_id: str) -> QuotaStatus:
    now = datetime.now(timezone.utc)
    
    try:
        usage_record = (
            await db.execute(
                select(AIUsageTrackerTable)
                .where(AIUsageTrackerTable.user_id == user_id)
                .with_for_update()
            )
        ).scalar_one_or_none()

        # First AI request ever
        if usage_record is None:
            db.add(
                AIUsageTrackerTable(
                    user_id=user_id,
                    last_used=now,
                    state=AIRequestState.PENDING, #Column(Enum(AIRequestState) dw State needs enum obj 
                    current_request_id=request_id
                )
            )
            await db.commit()
            log_state(ReservationLog.AI_RESERVATION_CREATED, function="consume_ai_quota", user_id=user_id, request_id=request_id)
            return QuotaStatus.ALLOWED


        last_used = usage_record.last_used
        if last_used.tzinfo is None:
            last_used = last_used.replace(
                tzinfo=timezone.utc
            )
        

        if usage_record.state == AIRequestState.PENDING:
            
            if now - last_used > timedelta(minutes=5):
                usage_record.state = AIRequestState.FAILED

                usage_record.last_used = (
                    now - timedelta(hours=24)
                )
                usage_record.current_request_id = None
            else:
                await db.rollback()
                log_state(GatewayLog.AI_REQUEST_COLLISION, function="consume_ai_quota", user_id=user_id, request_id=request_id)
                return QuotaStatus.COLLISION
        

        # 24 hour quota check
        if usage_record.state == AIRequestState.COMPLETED and (now - last_used < timedelta(hours=24)):
            await db.rollback()
            log_state(event=GatewayLog.AI_QUOTA_EXHAUSTED, function="consume_ai_quota", user_id=user_id, request_id=request_id)
            return QuotaStatus.EXHAUSTED #already used!
        
        
        #if first call creating a reservatiton
        usage_record.last_used = now
        usage_record.state = AIRequestState.PENDING
        usage_record.current_request_id = request_id
        await db.commit()

        log_state(ReservationLog.AI_RESERVATION_CREATED, function="consume_ai_quota", user_id=user_id, request_id=request_id)
        return QuotaStatus.ALLOWED

    except IntegrityError as e:
        """
        potential future issue:
            Right now, every IntegrityError is assumed to mean "two requests happened at the same time" (collision).
            As the database grows, IntegrityError can also happen because of missing required data, broken foreign keys, or new constraints. 
            If we always return COLLISION, real database bugs will be hidden and much harder to debug.
            
            potential solution:
                Later, check what kind of IntegrityError actually happened.
                If it's a UNIQUE constraint violation → return COLLISION.
                Otherwise, let the exception be handled normally (or raise a DatabaseException) so real database bugs aren't hidden. or make custom exception 
        """
        
        await db.rollback()
        log_state(GatewayLog.AI_REQUEST_COLLISION, function="consume_ai_quota", user_id=user_id, request_id=request_id, exc=e)
        return QuotaStatus.COLLISION

async def release_ai_reservation(db: AsyncSession, user_id: int, request_id: str, success: bool) -> None:
    try:
        usage_record = (
            await db.execute(
                select(AIUsageTrackerTable)
                .where(AIUsageTrackerTable.user_id == user_id)
                .with_for_update()
            )
        ).scalar_one_or_none()

        if usage_record is None:
            return

        if usage_record.current_request_id != request_id:
            return

        if success:
            usage_record.state = AIRequestState.COMPLETED #
            usage_record.current_request_id = None
            log_state(ReservationLog.AI_RESERVATION_COMPLETED, function="consume_ai_quota", user_id=user_id, request_id=request_id)
            
        else:
            usage_record.state = AIRequestState.FAILED 

            # Refund quota
            usage_record.last_used = (
                datetime.now(timezone.utc)
                - timedelta(hours=24)
            )
            usage_record.current_request_id = None
            log_state(ReservationLog.AI_RESERVATION_FAILED, function="consume_ai_quota", user_id=user_id, request_id=request_id)
        await db.commit()

    except Exception as e:
        await db.rollback()
        log_state(ReservationLog.AI_RESERVATION_FAILED, level=LogState.EXCEPTION ,function="consume_ai_quota", user_id=user_id, request_id=request_id)

        raise



router = APIRouter(
    prefix="/ai",
    tags=["AI"],
    dependencies=[Depends(get_user_jwt_payload)] #just in case
)


#New Rephrase:
@router.post("/rephrase", response_model=RephraseOutput_route)
async def rephrase_text(
    payload: RephraseRequest_route,
    db: AsyncSession = Depends(get_db),
    user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload) 
) -> RephraseOutput_route:

    request_id = str(uuid4())
    user_id = user_jwt_payload.user_id
    
    quota = await consume_ai_quota(db, user_id, request_id)
    Quota_check(quota)

    success = False 
    try:
        result: APIResponse = await rephraser(
            model,
            payload.text,
            payload.tone
        )
        success = not is_system_failure(result) 
    except Exception:
        raise 

    finally:
        await release_ai_reservation(
            db,
            user_id,
            request_id,
            success=success
        )




@router.post("/summary", response_model=SummaryOut_route)
async def summary_text(payload: SummaryRequest_route,
                        db: AsyncSession = Depends(get_db),
                        user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload) 
) -> SummaryOut_route:
    
    request_id = str(uuid4())
    user_id = user_jwt_payload.user_id
    
    quota = await consume_ai_quota(db, user_id, request_id)
    Quota_check(quota)
    
    success = False
    try:
        result: APIResponse = await summry_ai(
            model, 
            payload.text
        )
        success = not is_system_failure(result) #if result fails then we go in finally, if it doesnt we go check is_system_failure and get a bool and return (so ig we can remove expt fully in next route ill!)
        return handle_service_response(result, AIServiceException)
    except Exception:
        success = False 
        raise
    
    finally:
        await release_ai_reservation(db, user_id, request_id, success = success)



@router.post("/sentiment_analysis", response_model=SentimentAnalysisOut_route)
async def sentiment_analysis(payload: SentimentAnalysisRequest_route, 
                            db: AsyncSession = Depends(get_db),
                            user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload) 
) -> SentimentAnalysisOut_route:
    
    request_id = str(uuid4())
    user_id = user_jwt_payload.user_id
    
    quota = await consume_ai_quota(db, user_id, request_id)
    Quota_check(quota)
    
    success = False
    try:
        result: APIResponse = await sentiment_analysis_ai(
            model, 
            payload.text
        )
        success = not is_system_failure(result)
        return handle_service_response(result, AIServiceException)
    finally:
        await release_ai_reservation(db, user_id, request_id, success = success)
    



@router.post("/title_gen", response_model=Title_genOut_Route)
async def title_gen(payload: Title_genRequest_Route, db: AsyncSession = Depends(get_db), user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload)) -> Title_genOut_Route:
    
    request_id = str(uuid4())
    user_id = user_jwt_payload.user_id
    
    quota = await consume_ai_quota(db, user_id, request_id)
    Quota_check(quota)
    
    success = False 
    try:
        result: APIResponse = await generate_titles(
            model, 
            payload.text
        ) 
        success = not is_system_failure(result)
        return handle_service_response(result, AIServiceException) #either i get result or AIServiceException 
    finally:
        await release_ai_reservation(db, user_id, request_id, success = success)
