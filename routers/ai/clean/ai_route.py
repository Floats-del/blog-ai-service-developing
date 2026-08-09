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



@router.post("/summary", response_model=All_worker_starter_responce)
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

