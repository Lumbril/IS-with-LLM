import time
import requests

BASE_URL = "http://backend:8000"

USERNAME = "test_user"
PASSWORD = "password123"
EMAIL = "test@test.com"


def wait_for_backend():
    print("Waiting for backend...")
    while True:
        try:
            requests.get(f"{BASE_URL}/docs")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(2)
    print("Backend is ready")


def register():
    print("Registering user")

    r = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": USERNAME,
            "email": EMAIL,
            "password": PASSWORD
        }
    )

    print("Register status:", r.status_code)


def sql_injection():
    print("SQL Injection attempt")

    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "' OR '1'='1",
            "password": "test"
        }
    )

    print("SQLi status:", r.status_code)


def brute_force():
    print("Starting brute force")

    for i in range(10):
        r = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": USERNAME,
                "password": "wrong_password"
            }
        )

        print(f"Attempt {i+1}:", r.status_code)


if __name__ == "__main__":
    wait_for_backend()

    register()

    time.sleep(2)

    sql_injection()

    time.sleep(1)

    brute_force()

    print("Attack simulation finished")
