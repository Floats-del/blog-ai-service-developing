from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from db_tables.tables import AIUsageTrackerTable 
from utils.schemas import AIRequestState

from utils.logging.helper_log import log_state, LogState
from utils.logging.logEvents import (
    ReservationLog,
    GatewayLog
)
from utils.schemas import QuotaStatus




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
                    state=AIRequestState.PENDING, #
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
