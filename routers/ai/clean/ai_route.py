from core.rate_limiters.limiter_file import limiter
from core.rate_limiters.limiter_utils import RateLimits
from celery_worker.tasks.Ai_worker.Ai_worker import title_gen_task
from fastapi import status
from uuid import uuid4
from fastapi import APIRouter, Depends, Request, Response
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
from routers.ai.clean.ai_helpers import Quota_check
from routers.ai.clean.ai_route_utils import title_gen_worker_inishiator
from utils.schemas import AIGatewayContext, AIRequestState, LogContext, TaskResponse
from utils.ai_responce_handler import handle_service_response, is_system_failure

from utils.logging.helper_log import log_state, LogState
from utils.logging.logEvents import (
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
        
        
        # request already running! SO HE DOESNT OPEN NEW TAB AND SPAM US
        if usage_record.state == AIRequestState.PENDING:

            # If a reservation has been stuck for too long
            # (server crash, Ctrl+C, laptop sleep, etc.)
            # treat it as failed and allow a new request.
            
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
            usage_record.state = AIRequestState.COMPLETED #a helper const class which i use so i dont spelling msitake to insert any 3 filds in db 
                #dont do .value here! coz state column is Enum(AIRequestState) so it stores enum obj so dw
            usage_record.current_request_id = None
            log_state(ReservationLog.AI_RESERVATION_COMPLETED, function="consume_ai_quota", user_id=user_id, request_id=request_id)
            
        else:
            usage_record.state = AIRequestState.FAILED #WE DID ALL OF THIS JUST SO WE DONT UNFAIRLY TAKE HIS 24HRS AWAY! DUR TO GROQ'S SERVER ERRORS!

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
        #i had reservation failed, but in try i also have db so what if error comes form db and not reservation?
            #IN FUTURE EITHER SAPRATE TRY OR KEEP IT APP_EXCEPTION

        raise



router = APIRouter(
    prefix="/ai",
    tags=["AI"],
    dependencies=[Depends(get_user_jwt_payload)] #just in case
)




#A concern for future:
"""
However, there is a hidden architectural edge-case you should be aware of: Database Operations within release_ai_reservation can fail too.
If release_ai_reservation() performs a database operation (like an UPDATE on the user's quota table) and your Postgres connection blinks out right there, release_ai_reservation 
will raise a SQLAlchemy/Database Exception.

If that happens after the AI succeeded:
The AI worked perfectly.
release_ai_reservation raises a DB exception.
The exception bubbles up, skipping handle_service_response(result, AIServiceException).
Your global unexpected_exception_handler catches it and returns a 500 Internal Server Error to the user.

The Bug: The user gets a 500 error, but their quota state might be stuck in "reserved" and never finalized.

solution:
Learn advanced backend topics:

retries
idempotency
background workers
distributed systems
sharding
caching
reliable messaging

then come back here to fix this! coz rn idh tools for this!
"""






#routes 
#OLD rephrase:

# @router.post("/rephrase", response_model=RephraseOutput_route)
# async def rephrase_text(
#     payload: RephraseRequest_route,
#     db: AsyncSession = Depends(get_db),
#     quota_guard_data: AIGatewayContext = Depends(ai_gateway) #using this idh to call jwt here! since all checking and stuff is done by ai_gatway ;)
# ) -> RephraseOutput_route:

#     request_id = quota_guard_data.request_id
#     user_id = quota_guard_data.user_id

#     try:
#         result: APIResponse = await rephraser(
#             model,
#             payload.text,
#             payload.tone
#         )
    
#     #all above in this route deals with if can he or can he not make ai req! bellow is checking if erros is system error or user doing some bs

#     except Exception:
#         #System failure => Refund quota (this perticular part checks if any system error happend! (like for me groq failed coz 100k done))
#             #since this catches ai_service exception which can only mean my fault! so we call release_ai_reservation to give him his quota back
#         await release_ai_reservation(db, user_id, request_id, success=False)
#         raise #since this is an Exception which i made to handle by unexpected_exception_handler -> JSONResponse ez ;)


#     #since if exception happend last time! we 100% gave him his quota back!
#         #now if we reach here that means we got APIResponce back! which is checked by is_system_failure() 
#             #which basically sees, that if result.succes is fasle and if result.error_code is of system_error_codes,
#                 #if yes! then we made mistake again! (rare case coz we have exception above!) even if happens so we get returned True and due to not in biggning
#                     #succes=False and we give quota back! he can get a try again msg form front_end (client side coz we finna be doing stuff there too dw!)
#     await release_ai_reservation( 
#         db,
#         user_id,
#         request_id,
#         success = not is_system_failure(result) #we see if the rephraser gave system error, coz if system failure success=Flase, and on flase we dont 24 charge user,         
#             #coz our bad bro.. but if its his fault this becomes true, so we charge him 24hrs
#     ) 
#     #one thing that bugs me rn is: release_ai_reservation() returns none too! so what if outside exception
#     #such a thing happens that none is returned? 
#     #Ans) well that will just be standalone None dw lol, coz bellw is handle_ai_responce() which checks if we succeded else AppException ;)
    
#     return handle_service_response(result, AIServiceException)




#New Rephrase:
@router.post("/rephrase", response_model=RephraseOutput_route)
@limiter.limit(RateLimits.AI.DEFAULT)  #essentially RateLimits.AI.DEFAULT means 30/min
async def rephrase_text(
    request: Request, response: Response, 
    payload: RephraseRequest_route,
    db: AsyncSession = Depends(get_db),
    user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload) 
) -> RephraseOutput_route:

    request_id = str(uuid4())
    user_id = user_jwt_payload.user_id
    
    quota = await consume_ai_quota(db, user_id, request_id)
    Quota_check(quota)

    success = False #default to failure so if anything unexpected happens user gets refunded
    try:
        result: APIResponse = await rephraser(
            model,
            payload.text,
            payload.tone
        )

        #since if exception happend last time! we 100% gave him his quota back!
        #now if we reach here that means we got APIResponce back! which is checked by is_system_failure()
            #which basically sees, that if result.succes is fasle and if result.error_code is of system_error_codes,
                #if yes! then we made mistake again! (rare case coz we have exception above!) even if happens so we get returned True and due to not in biggning
                    #succes=False and we give quota back! he can get a try again msg form front_end (client side coz we finna be doing stuff there too dw!)
        success = not is_system_failure(result) #we see if the rephraser gave system error, coz if system failure success=False, and on false we dont 24hr charge user,
                                                #coz our bad bro.. but if its his fault this becomes true, so we charge him 24hrs

        #one thing that bugs me rn is: handle_service_response() can also throw AppException!
        #but now thats fine coz finally ALWAYS runs before exception leaves this function.
        return handle_service_response(result, AIServiceException)
        #BTW return can also stay in try coz if any above it in try errors it wont return

    except Exception:
        #System failure => Refund quota (this perticular part checks if any system error happend! (like for me groq failed coz 100k done))
            #since this catches ai_service exception which can only mean my fault! so we call release_ai_reservation to give him his quota back
        success = False
        raise #since this is an Exception which i made to handle by unexpected_exception_handler -> JSONResponse ez ;)
        #initially i didnt had finally coz say if any isse in try happens we come in except and raise execits! we never go to release_ai_reservation! but now we have finally
            #so no more that issue!

    finally:
        #ALWAYS runs.
        #Whether AI succeeds, AI fails, handle_service_response() raises,
        #FastAPI response validation explodes, or literally anything else.
        #This guarantees we never leave a reservation stuck in PENDING.
        await release_ai_reservation(
            db,
            user_id,
            request_id,
            success=success
        )



#start here fixing this! (DO  these, then fix bellow routes like u did for above)
# 1) looging fix in all Ai servixes (core folder done)
# 2) ive standarized error code and APIService faliure's error codes via enum in rephraser do same for all other Ai services

@router.post("/summary", response_model=SummaryOut_route)
@limiter.limit(RateLimits.AI.DEFAULT)
async def summary_text(
    request: Request, response: Response, 
    payload: SummaryRequest_route,
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
@limiter.limit(RateLimits.AI.DEFAULT)
async def sentiment_analysis(request: Request, response: Response, payload: SentimentAnalysisRequest_route, 
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
    






@router.post("/title_gen", status_code=status.HTTP_202_ACCEPTED, response_model=TaskResponse)
@limiter.limit(RateLimits.AI.DEFAULT)
async def title_gen(request: Request, response: Response, payload: Title_genRequest_Route, user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> TaskResponse:
    return TaskResponse(task_id=await title_gen_worker_inishiator(user_jwt_payload, db, payload))



"""
flow (easy):
Request
    ↓
JWT
    ↓
Pydantic Validation
    ↓
Route Starts
    ↓
consume_ai_quota()
    ↓
PENDING
    ↓
AI Provider
    ↓
APIResponse
    ↓
handle_service_response()
    ↓
finally
    ↓
release_ai_reservation()
    ↓
COMPLETED
    ↓
HTTP 200

Flow (full):
Client (Postman / Frontend)
        │
        ▼
FastAPI Router
        │
        ▼
JWT Authentication
(get_user_jwt_payload)
        │
        │  ❌ Invalid token → 401
        ▼
Pydantic Validation
(Request body validation)
        │
        │  ❌ Bad JSON / Missing fields → 422
        │     (Route NEVER starts)
        ▼
Route Starts
(title_gen / summary / rephrase / ...)
        │
        ▼
Generate request_id
(uuid4())
        │
        ▼
consume_ai_quota()
        │
        ├── ALLOWED
        │       │
        │       ▼
        │   Reservation created
        │
        ├── EXHAUSTED
        │       │
        │       ▼
        │   429 Too Many Requests
        │
        └── COLLISION
                │
                ▼
          409 Conflict
                │
        (Route exits here)
                ▼
AI Service
(generate_titles /
 summary_ai /
 rephraser /
 etc.)
        │
        ▼
APIResponse
(success / failure)
        │
        ▼
success = not is_system_failure(...)
        │
        ▼
handle_service_response()
        │
        ├── Success
        │       │
        │       ▼
        │   Return response
        │
        └── Failure
                │
                ▼
        Raise AIServiceException
                │
                ▼
finally
        │
        ▼
release_ai_reservation()
        │
        ├── success=True
        │       │
        │       ▼
        │   state = COMPLETED
        │
        └── success=False
                │
                ▼
          state = FAILED
          refund quota
          clear request_id
        │
        ▼
Global Exception Handler
(if exception happened)
        │
        ▼
HTTP Response
"""



#testing:
# @router.post("/internal/title_gen", response_model=Title_genOut_Route)
# async def internal_title_gen(
#     payload: Title_genRequest_Route
# ):
#     result = await generate_titles(
#         model,
#         payload.text
#     )

#     return handle_service_response(
#         result,
#         AIServiceException
#     )