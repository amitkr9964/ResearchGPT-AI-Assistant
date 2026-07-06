"""Authentication service."""

from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.jwt_handler import create_access_token
from backend.auth.password import hash_password, verify_password
from backend.database.models import User
from backend.models.schemas import UserLogin, UserResponse, UserSignup, UserUpdate


class AuthService:
    @staticmethod
    async def signup(db: AsyncSession, data: UserSignup) -> User:
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        result = await db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def login(db: AsyncSession, data: UserLogin) -> tuple[User, str]:
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token = create_access_token({"sub": str(user.id)})
        return user, token

    @staticmethod
    async def update_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.dark_mode is not None:
            user.dark_mode = data.dark_mode
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    def to_response(user: User) -> UserResponse:
        return UserResponse.model_validate(user)
