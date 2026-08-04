from uuid import uuid4
from celery_worker.tasks.Ai_worker.Ai_worker import title_gen_task
from routers.ai.clean.ai_helpers import Quota_check
from routers.ai.clean.ai_route_copy import consume_ai_quota
from utils.schemas import Title_genRequest_Route, TokenDataSchema
from sqlalchemy.ext.asyncio import AsyncSession 

async def title_gen_worker_inishiator(user_jwt_payload: TokenDataSchema, db: AsyncSession, payload: Title_genRequest_Route) -> str:
    request_id = str(uuid4())
    user_id = user_jwt_payload.user_id

    quota = await consume_ai_quota(db, user_id, request_id)
    Quota_check(quota)
    
    task = title_gen_task.delay(payload.text, user_id, request_id)
    return task.id
    