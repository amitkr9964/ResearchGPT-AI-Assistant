"""Authentication API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.database.database import get_db
from backend.database.models import User
from backend.models.schemas import TokenResponse, UserLogin, UserResponse, UserSignup, UserUpdate
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(data: UserSignup, db: AsyncSession = Depends(get_db)):
    user = await AuthService.signup(db, data)
    return AuthService.to_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user, token = await AuthService.login(db, data)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return AuthService.to_response(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await AuthService.update_profile(db, current_user, data)
    return AuthService.to_response(user)
