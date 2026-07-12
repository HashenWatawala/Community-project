from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, status
import traceback
from passlib.context import CryptContext
from jose import jwt

from app.schemas.user_schema import UserCreate, UserOut, LoginPayload, TokenResponse
from app.models.user_model import get_user_by_username, get_user_by_email, create_user
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/auth", tags=["auth"])


def create_access_token(subject: str, expires_delta: int | None = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=(expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate) -> Any:
    try:
        # check existing username/email
        existing = await get_user_by_username(payload.username)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        existing_email = await get_user_by_email(payload.email)
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        truncated = payload.password.encode('utf-8')[:72].decode('utf-8', errors='ignore')        
        hashed = pwd_context.hash(truncated)
        user_doc = payload.model_dump()
        user_doc["hashed_password"] = hashed
        user_doc.pop("password", None)

        user = await create_user(user_doc)
        # remove hashed_password before returning
        user.pop("hashed_password", None)
        return UserOut(**user)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - unexpected server error
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginPayload) -> Any:
    try:
        user = await get_user_by_username(payload.username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        hashed = user.get("hashed_password")
        if not hashed or not pwd_context.verify(payload.password, hashed):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(subject=user["username"])
        # prepare user out
        user_out = {k: v for k, v in user.items() if k != "hashed_password"}
        return TokenResponse(access_token=access_token, user=UserOut(**user_out))
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - unexpected server error
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
