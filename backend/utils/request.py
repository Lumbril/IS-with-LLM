from fastapi import Request


def get_client_ip(request: Request):

    forwarded = request.headers.get("x-forwarded-for")

    if forwarded:
        return forwarded.split(",")[0]

    return request.client.host
