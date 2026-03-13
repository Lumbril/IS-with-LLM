import json

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import settings
from models import Log
from models import Anomaly

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def analyze_logs_with_llm(db: AsyncSession):
    result = await db.execute(
        select(Log).order_by(Log.created_at.desc()).limit(50)
    )
    logs = result.scalars().all()
    if not logs:
        return

    logs_data = [
        {"event": log.event_type, "ip": log.ip_address, "details": log.details}
        for log in logs
    ]

    prompt = f"""
    Вы — аналитик по кибербезопасности.

    Проанализируйте следующие события входа в систему и определите, есть ли атака.

    Логи:
    {json.dumps(logs_data, indent=2, ensure_ascii=False)}

    Верните результат в формате JSON:

    {{
     "severity": "низкий|средний|высокий",
     "description": "описание атаки",
     "ip_address": "IP-адрес, если известен"
    }}

    Если аномалий нет, верните:
    {{"severity":"none"}}
    """

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                })
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.RequestError, json.JSONDecodeError):
            return

    try:
        content = data["choices"][0]["message"]["content"][7:-3]
        anomaly_data = json.loads(content)
    except (KeyError, IndexError, json.JSONDecodeError):
        return

    if anomaly_data.get("severity") == "none":
        return

    anomaly = Anomaly(
        severity=anomaly_data["severity"],
        description=anomaly_data["description"],
        ip_address=anomaly_data.get("ip_address"),
    )

    db.add(anomaly)
    await db.commit()
