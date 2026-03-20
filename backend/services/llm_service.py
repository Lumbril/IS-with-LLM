import json

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from config import settings
from models import Log
from models import Anomaly

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def analyze_logs_with_llm(db: AsyncSession):
    result = await db.execute(
        select(Log).order_by(desc(Log.created_at)).limit(50)
    )
    logs = result.scalars().all()
    if not logs:
        return

    logs_data = [
        {"event": log.event_type, "ip": log.ip_address, "details": log.details}
        for log in logs
    ]

    prompt_general = f"""
Вы — аналитик по кибербезопасности.

Проанализируйте следующие события входа в систему и определите, есть ли атака (SQL-инъекция, брутфорс).

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
                        {"role": "user", "content": [{"type": "text", "text": prompt_general}]}
                    ],
                }),
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            anomaly_data = json.loads(content)
        except Exception:
            anomaly_data = {"severity": "none"}

    if anomaly_data.get("severity") != "none":
        anomaly = Anomaly(
            severity=anomaly_data["severity"],
            description=anomaly_data["description"],
            ip_address=anomaly_data.get("ip_address"),
        )
        db.add(anomaly)
        await db.commit()

    result = await db.execute(
        select(Log).where(Log.event_type == "login_success").order_by(Log.created_at)
    )
    successful_logs = result.scalars().all()

    for log in successful_logs:
        window_result = await db.execute(
            select(Log)
            .order_by(Log.created_at)
            .where(Log.id.between(log.id - 25, log.id + 25))
        )
        window_logs = window_result.scalars().all()
        window_data = [
            {"event": l.event_type, "ip": l.ip_address, "details": l.details}
            for l in window_logs
        ]
        prompt_spray = f"""
Вы — аналитик по кибербезопасности.

Проверьте следующие события на попытки pass spray (много неудачных входов на один аккаунт с разных IP).

Логи:
{json.dumps(window_data, indent=2, ensure_ascii=False)}

Верните результат в формате JSON:

{{
 "severity": "низкий|средний|высокий",
 "description": "описание атаки",
 "ip_address": "IP-адрес атакующего"
}}

Если аномалий нет, верните:
{{"severity":"none"}}
"""
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
                        {"role": "user", "content": [{"type": "text", "text": prompt_spray}]}
                    ],
                }),
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            spray_data = json.loads(content)
        except Exception:
            spray_data = {"severity": "none"}

        if spray_data.get("severity") != "none":
            anomaly = Anomaly(
                severity=spray_data["severity"],
                description=spray_data["description"],
                ip_address=spray_data.get("ip_address"),
            )
            db.add(anomaly)
            await db.commit()
