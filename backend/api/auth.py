from fastapi import Request

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.session import get_db
from models import User, SecurityEvent
from schemas.auth import *
from services.security_log_service import create_log, failed_login_attempts
from utils import get_client_ip, detect_sql_injection
from utils.security import hash_password, verify_password
from utils.jwt import create_access_token, create_refresh_token
from api.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(User.username == data.username)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent")

    if detect_sql_injection(data.username):
        await create_log(
            db,
            SecurityEvent.SQL_INJECTION_ATTEMPT,
            ip,
            details={"username": data.username}
        )

    result = await db.execute(
        select(User).where(User.username == data.username)
    )

    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        await create_log(
            db,
            SecurityEvent.LOGIN_FAILED,
            ip,
            user_agent=user_agent,
            details={"username": data.username}
        )

        attempts = await failed_login_attempts(db, ip)

        if attempts > 5:
            await create_log(
                db,
                SecurityEvent.BRUTE_FORCE,
                ip,
                user_agent=user_agent,
                details={"username": data.username}
            )

        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.last_login_ip and user.last_login_ip != ip:
        await create_log(
            db,
            SecurityEvent.IP_CHANGED,
            ip,
            user_id=user.id,
            user_agent=user_agent,
            details={"old_ip": user.last_login_ip}
        )

    user.last_login_ip = ip

    await create_log(
        db,
        SecurityEvent.LOGIN_SUCCESS,
        ip,
        user_agent=user_agent,
        user_id=user.id
    )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
