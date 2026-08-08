from fastapi import APIRouter
from celery_worker.tasks.Ai_worker.Ai_worker_utils import get_worker_result
from celery_worker.tasks.worker_utils import worker_result_handler
from utils.schemas import APIResponse, RephraseOutput_route, SentimentAnalysisOut_route, SummaryOut_route, Title_genOut_Route


router = APIRouter(tags=["AI-Pool"]) #it gets own router

#in future if u get time ake sure that ... | dict is under a schama as well as dict holds Title_genOut_Route init!
@router.get("/title_gen_worker/{task_id}")
async def get_title_gen_worker_result(task_id: str) -> Title_genOut_Route | dict:
    worker_responce: APIResponse = get_worker_result(task_id)
    return worker_result_handler(worker_responce)

@router.get("/sentiment_analysis_worker/{task_id}")
async def get_sentiment_analysis_worker_result(task_id: str) -> SentimentAnalysisOut_route | dict:
    worker_responce: APIResponse = get_worker_result(task_id)
    return worker_result_handler(worker_responce)

@router.get("/summary_ai_worker/{task_id}")
async def get_summary_ai_worker_result(task_id: str) -> SummaryOut_route | dict:
    worker_responce: APIResponse = get_worker_result(task_id)
    return worker_result_handler(worker_responce)

@router.get("/rephras_ai_worker/{task_id}")
async def get_rephrase_ai_worker_result(task_id: str) -> RephraseOutput_route | dict:
    worker_responce: APIResponse = get_worker_result(task_id)
    return worker_result_handler(worker_responce)