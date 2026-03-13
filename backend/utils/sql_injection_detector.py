import re


SQL_PATTERNS = [
    r"(\bor\b|\band\b).*=.*",
    r"union\s+select",
    r"drop\s+table",
    r"sleep\(",
    r"--",
    r";"
]


def detect_sql_injection(value: str):

    value = value.lower()

    for pattern in SQL_PATTERNS:
        if re.search(pattern, value):
            return True

    return False
