"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, status_code=201)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    user = AuthService.register_user(db, user_data)
    token_data = AuthService.authenticate_user(
        db, UserLogin(email=user_data.email, password=user_data.password)
    )
    return token_data


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and get access token."""
    return AuthService.authenticate_user(db, login_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return current_user
