from celery.result import AsyncResult
from celery_worker.celery_app import celery_app
from utils.APIResponce_error_code_enum import SYSTEM_ERROR_CODES
from utils.schemas import APIResponse



def get_worker_result(task_id: str) -> APIResponse:
    result = AsyncResult(
    task_id,
    app=celery_app
    )
    
    if result.state == "SUCCESS":
        data = {
            "task_id": task_id,
            "state": result.state,
            "ready": result.ready(),
            "successful": result.successful(),
            "failed": result.failed(),
            "result": result.result if result.successful() else None
        }
        return APIResponse(
            success=True,
            data=data,
            error_code=None,
            error_message=None
        )

    elif result.state == "FAILURE":
        data = {
            "status": "failed",
            "task_id": task_id,
            "state": result.state,
            "failed": True
        }
        return APIResponse(
            success=False,
            data=data,
            error_code=SYSTEM_ERROR_CODES.WORKER_PROCESS_FAILED.value,
            error_message=str(result.result)
        )
    
    elif result.state == "RETRY":
        data = {"status": "retrying", "task_id": task_id, "state": result.state, "failed": False}
        return APIResponse(
            success=False,
            data=data,
            error_code=SYSTEM_ERROR_CODES.WORKER_PROCESS_RETRYING.value,
            error_message="Due to previous result failure, Worker currently retrying"
        )
    else:
        data = {"status": "processing", "task_id": task_id, "state": result.state, "failed": False}
        return APIResponse(
            success=False,
            data=data,
            error_code=SYSTEM_ERROR_CODES.WORKER_IN_PROCESS.value,
            error_message="Worker currently in processing."
        )
    