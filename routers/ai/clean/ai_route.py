from core.rate_limiters.limiter_file import limiter
from core.rate_limiters.limiter_utils import RateLimits
from fastapi import status
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from db import get_db
from Oauth2 import get_user_jwt_payload
from datetime import datetime, timedelta, timezone
from db_tables.tables import AIUsageTrackerTable 
from routers.ai.clean.ai_route_utils import rephrase_ai_worker_inishiator, sentiment_analysis_worker_inishiator, summary_worker_inishiator, title_gen_worker_inishiator
from utils.schemas import AIRequestState, All_worker_starter_responce

from utils.logging.helper_log import log_state, LogState
from utils.logging.logEvents import (
    ReservationLog,
    GatewayLog
)

from utils.schemas import (
    RephraseRequest_route,
    SentimentAnalysisRequest_route,
    SummaryOut_route,
    SummaryRequest_route,
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
                    state=AIRequestState.PENDING, 
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
            return QuotaStatus.EXHAUSTED 
        
        

        usage_record.last_used = now
        usage_record.state = AIRequestState.PENDING
        usage_record.current_request_id = request_id
        await db.commit()

        log_state(ReservationLog.AI_RESERVATION_CREATED, function="consume_ai_quota", user_id=user_id, request_id=request_id)
        return QuotaStatus.ALLOWED

    except IntegrityError as e:
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
            usage_record.state = AIRequestState.COMPLETED 
            usage_record.current_request_id = None
            log_state(ReservationLog.AI_RESERVATION_COMPLETED, function="consume_ai_quota", user_id=user_id, request_id=request_id)
            
        else:
            usage_record.state = AIRequestState.FAILED 

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
    dependencies=[Depends(get_user_jwt_payload)] #just in case hehe
)





@router.post("/rephrase", response_model=All_worker_starter_responce)
@limiter.limit(RateLimits.AI.DEFAULT) 
async def rephrase_text(
    request: Request, response: Response, 
    payload: RephraseRequest_route,
    db: AsyncSession = Depends(get_db),
    user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload) 
) -> All_worker_starter_responce:
    return All_worker_starter_responce(task_id=await rephrase_ai_worker_inishiator(user_jwt_payload, db, payload))



@router.post("/summary", response_model=SummaryOut_route)
@limiter.limit(RateLimits.AI.DEFAULT)
async def summary_text(
    request: Request, response: Response, 
    payload: SummaryRequest_route,
    db: AsyncSession = Depends(get_db),
    user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload) 
) -> SummaryOut_route:
        return All_worker_starter_responce(task_id=await summary_worker_inishiator(user_jwt_payload, db, payload))


@router.post("/sentiment_analysis", response_model=All_worker_starter_responce)
@limiter.limit(RateLimits.AI.DEFAULT)
async def sentiment_analysis(request: Request, response: Response, payload: SentimentAnalysisRequest_route, 
                            db: AsyncSession = Depends(get_db),
                            user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload) 
) -> All_worker_starter_responce:
    return All_worker_starter_responce(task_id=await sentiment_analysis_worker_inishiator(user_jwt_payload, db, payload))


@router.post("/title_gen", status_code=status.HTTP_202_ACCEPTED, response_model=All_worker_starter_responce) 
@limiter.limit(RateLimits.AI.DEFAULT)
async def title_gen(request: Request, response: Response, payload: Title_genRequest_Route, user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> All_worker_starter_responce:
    return All_worker_starter_responce(task_id=await title_gen_worker_inishiator(user_jwt_payload, db, payload))

