import requests
import json

from config import settings

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
  },
  data=json.dumps({
    "model": settings.OPENROUTER_MODEL,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Привет как дела"
          }
        ]
      }
    ]
  })
)

message = response.json()["choices"][0]["message"]["content"]

print(message)
