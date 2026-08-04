import asyncio
import httpx
from Ai.title_gen import generate_titles
from celery_worker.tasks.Ai_worker.Ai_worker_utils import get_title_worker_result
from celery_worker.tasks.worker_utils import worker_result_handler
from core.exceptions import AIServiceException
from db import AsyncSessionLocal
from routers.ai.clean.ai_route_copy import release_ai_reservation
from utils.APIResponce_error_code_enum import SYSTEM_ERROR_CODES
from utils.ai_responce_handler import is_system_failure
from Ai.main import model
from celery_worker.celery_app import celery_app
from utils.schemas import APIResponse
from routers.ai.clean.ai_route_copy import router

#TITLE_GEN
async def _generate_title_async(text: str, user_id: str, request_id: str):
    async with AsyncSessionLocal() as db:                                                
        success = False
        try:
            result = await generate_titles(
                model,
                text
            )
            success = not is_system_failure(result)
            return result

        finally:
            await release_ai_reservation(db, user_id, request_id, success=success)


@celery_app.task(bind=True, max_retries=3, name="ai.title_generation") 
def title_gen_task(self, text: str, user_id: str, request_id: str): 
    try:
        return asyncio.run( #this exact command makes worker async!
            _generate_title_async(
                text,
                user_id,
                request_id
            )
        )
      
    except (
        httpx.TimeoutException, 
        ConnectionError,
        AIServiceException
    ) as exc:
        if exc.error_code in (
            SYSTEM_ERROR_CODES.AI_SERVICE_FAILURE.value 
                                                        
        ):
            raise self.retry(
                exc=exc,
                countdown=1
            )

@router.get("/title_gen/{task_id}")
async def get_result(task_id: str):
    worker_responce: APIResponse = get_title_worker_result(task_id, celery_app)
    return worker_result_handler(worker_responce)