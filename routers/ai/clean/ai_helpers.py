from fastapi import HTTPException
from utils.schemas import QuotaStatus


def Quota_check(quota: QuotaStatus) -> None:
    match quota:

        case QuotaStatus.ALLOWED:
            pass

        case QuotaStatus.EXHAUSTED:
            raise HTTPException(
                status_code=429,
                detail="Daily AI quota exhausted."
            )

        case QuotaStatus.COLLISION:
            raise HTTPException(
                status_code=409,
                detail="Another AI request is already in progress."
            )