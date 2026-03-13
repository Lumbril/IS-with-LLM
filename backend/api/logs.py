from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from services.llm_service import analyze_logs_with_llm
from database.session import get_db

router = APIRouter()


@router.post("/analyze")
async def analyze_logs(db: AsyncSession = Depends(get_db)):
    try:
        await analyze_logs_with_llm(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при анализе: {e}")

    result = await db.execute(
        text("SELECT COUNT(*) FROM anomalies WHERE created_at >= now() - interval '5 minutes';")
    )
    count = result.scalar_one_or_none() or 0

    return {"message": "Анализ завершён", "anomalies_created": count}
