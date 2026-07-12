from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    fullName: str
    username: str
    nic: str
    email: EmailStr
    role: str = "teacher"
    password: str


class UserOut(BaseModel):
    id: str
    fullName: str
    username: str
    nic: str
    email: EmailStr
    role: str


class LoginPayload(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserOut]
