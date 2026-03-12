from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.session import get_db
from models import User
from schemas.auth import *
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
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

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
