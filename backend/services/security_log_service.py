from typing import Optional, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Log, SecurityEvent


async def create_log(
    db: AsyncSession,
    event_type: str,
    ip: str,
    user_id: Optional[int] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict] = None
):

    log = Log(
        user_id=user_id,
        event_type=event_type,
        ip_address=ip,
        user_agent=user_agent,
        details=details
    )

    db.add(log)
    await db.commit()


async def failed_login_attempts(
    db: AsyncSession,
    ip: str
):

    result = await db.execute(
        select(func.count())
        .select_from(Log)
        .where(
            Log.ip_address == ip,
            Log.event_type == SecurityEvent.LOGIN_FAILED
        )
    )

    return result.scalar()
