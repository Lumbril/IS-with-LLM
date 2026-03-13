from enum import Enum


class SecurityEvent(str, Enum):

    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    IP_CHANGED = "ip_changed"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
