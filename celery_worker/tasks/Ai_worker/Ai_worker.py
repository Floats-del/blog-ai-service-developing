import asyncio
import httpx
from Ai.Ai_rephrase_content import rephraser
from Ai.sentiment_analysis import sentiment_analysis_ai
from Ai.summry_ai import summry_ai
from Ai.title_gen import generate_titles
from celery_worker.tasks.Ai_worker.Ai_worker_utils import get_worker_result
from celery_worker.tasks.worker_utils import worker_result_handler
from core.exceptions import AIServiceException
from db import AsyncSessionLocal
from routers.ai.clean.ai_route import release_ai_reservation
from utils.APIResponce_error_code_enum import SYSTEM_ERROR_CODES
from utils.ai_responce_handler import is_system_failure
from Ai.main import model
from celery_worker.celery_app import celery_app
from utils.schemas import APIResponse, RephraseOutput_route, SentimentAnalysisOut_route, SummaryOut_route, Title_genOut_Route
from routers.ai.clean.ai_route import router

#title gen one
async def generate_title_task_async(text: str, user_id: str, request_id: str):
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


@celery_app.task(bind=True, max_retries=3, name="ai.title_generation_worker") 
def title_gen_task(self, text: str, user_id: str, request_id: str): 
    try:
        return asyncio.run( 
            generate_title_task_async(
                text,
                user_id,
                request_id
            )
        )
    except AIServiceException as exc:
        if exc.error_code == SYSTEM_ERROR_CODES.AI_SERVICE_FAILURE.value: 
            raise self.retry(exc=exc, countdown=1)
    
    except (
        httpx.TimeoutException,
        ConnectionError,
    ) as exc:
        raise self.retry(exc=exc, countdown=1)

@router.get("/title_gen_worker/{task_id}")
async def get_title_gen_worker_result(task_id: str) -> Title_genOut_Route:
    worker_responce: APIResponse = get_worker_result(task_id)
    return worker_result_handler(worker_responce)



#sentiment_analysis one:
async def sentiment_analysis_task_async(text: str, user_id: str, request_id: str):
    async with AsyncSessionLocal() as db:       
        success = False
        try:
            result = await sentiment_analysis_ai(
                model,
                text
            )
            success = not is_system_failure(result)
            return result

        finally:
            await release_ai_reservation(db, user_id, request_id, success=success)


@celery_app.task(bind=True, max_retries=3, name="ai.sentiment_analysis_worker") 
def sentiment_analysis_task(self, text: str, user_id: str, request_id: str):
    try:
        return asyncio.run( 
            sentiment_analysis_task_async(
                text,
                user_id,
                request_id
            )
        )
    except AIServiceException as exc:
        if exc.error_code == SYSTEM_ERROR_CODES.AI_SERVICE_FAILURE.value:
            raise self.retry(exc=exc, countdown=1)

    except (
        httpx.TimeoutException,
        ConnectionError,
    ) as exc:
        raise self.retry(exc=exc, countdown=1)

@router.get("/sentiment_analysis_worker/{task_id}")
async def get_sentiment_analysis_worker_result(task_id: str) -> SentimentAnalysisOut_route:
    worker_responce: APIResponse = get_worker_result(task_id)
    return worker_result_handler(worker_responce)



#summary one:
async def summary_ai_task_async(text: str, user_id: str, request_id: str):
    async with AsyncSessionLocal() as db:       
        success = False
        try:
            result = await summry_ai(
                model,
                text
            )
            success = not is_system_failure(result)
            return result

        finally:
            await release_ai_reservation(db, user_id, request_id, success=success)

@celery_app.task(bind=True, max_retries=3, name="ai.summary_ai_worker") 
def summary_ai_task(self, text: str, user_id: str, request_id: str):
    try:
        return asyncio.run( 
            summary_ai_task_async(
                text,
                user_id,
                request_id
            )
        )
    except AIServiceException as exc:
        if exc.error_code == SYSTEM_ERROR_CODES.AI_SERVICE_FAILURE.value:
            raise self.retry(exc=exc, countdown=1)

    except (
        httpx.TimeoutException,
        ConnectionError,
    ) as exc:
        raise self.retry(exc=exc, countdown=1)

@router.get("summary_ai_worker/{task_id}")
async def get_summary_ai_worker_result(task_id: str) -> SummaryOut_route:
    worker_responce: APIResponse = get_worker_result(task_id)
    return worker_result_handler(worker_responce)


#rephraser one:
async def rephraser_ai_task_async(text: str, user_id: str, request_id: str):
    async with AsyncSessionLocal() as db:       
        success = False
        try:
            result = await rephraser(
                model,
                text
            )
            success = not is_system_failure(result)
            return result

        finally:
            await release_ai_reservation(db, user_id, request_id, success=success)

@celery_app.task(bind=True, max_retries=3, name="ai.rephraser_ai_worker") 
def rephraser_ai_task(self, text: str, user_id: str, request_id: str):
    try:
        return asyncio.run( 
            rephraser_ai_task_async(
                text,
                user_id,
                request_id
            )
        )
    except AIServiceException as exc:
        if exc.error_code == SYSTEM_ERROR_CODES.AI_SERVICE_FAILURE.value:
            raise self.retry(exc=exc, countdown=1)

    except (
        httpx.TimeoutException,
        ConnectionError,
    ) as exc:
        raise self.retry(exc=exc, countdown=1)
            
@router.get("rephras_ai_worker/{task_id}")
async def get_rephrase_ai_worker_result(task_id: str) -> RephraseOutput_route:
    worker_responce: APIResponse = get_worker_result(task_id)
    return worker_result_handler(worker_responce)
