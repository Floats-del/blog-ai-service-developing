from uuid import uuid4
from celery_worker.tasks.Ai_worker.Ai_worker import title_gen_task, sentiment_analysis_task, summary_ai_task, rephraser_ai_task
from routers.ai.clean.ai_helpers import Quota_check
from routers.ai.clean.ai_reservation_and_consume import consume_ai_quota
from utils.schemas import RephraseRequest_route, SentimentAnalysisRequest_route, SummaryRequest_route, Title_genRequest_Route, TokenDataSchema
from sqlalchemy.ext.asyncio import AsyncSession 


async def title_gen_worker_inishiator(user_jwt_payload: TokenDataSchema, db: AsyncSession, payload: Title_genRequest_Route) -> str:
    request_id = str(uuid4())
    user_id = user_jwt_payload.user_id

    quota = await consume_ai_quota(db, user_id, request_id)
    Quota_check(quota)
    
    task = title_gen_task.delay(payload.text, user_id, request_id)
    return task.id

async def sentiment_analysis_worker_inishiator(user_jwt_payload: TokenDataSchema, db: AsyncSession, payload: SentimentAnalysisRequest_route):
    request_id = str(uuid4())
    user_id = user_jwt_payload.user_id

    quota = await consume_ai_quota(db, user_id, request_id)
    Quota_check(quota)
    
    task = sentiment_analysis_task.delay(payload.text, user_id, request_id)
    return task.id 


async def summary_worker_inishiator(user_jwt_payload: TokenDataSchema, db: AsyncSession, payload: SummaryRequest_route):
    request_id = str(uuid4())
    user_id = user_jwt_payload.user_id

    quota = await consume_ai_quota(db, user_id, request_id)
    Quota_check(quota)
    
    task = summary_ai_task.delay(payload.text, user_id, request_id)
    return task.id 


async def rephrase_ai_worker_inishiator(user_jwt_payload: TokenDataSchema, db: AsyncSession, payload: RephraseRequest_route):
    request_id = str(uuid4())
    user_id = user_jwt_payload.user_id

    quota = await consume_ai_quota(db, user_id, request_id)
    Quota_check(quota)
    
    task = rephraser_ai_task.delay(payload.text, user_id, request_id)
    return task.id 