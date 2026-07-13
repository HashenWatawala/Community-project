from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class TeacherBase(BaseModel):
    fullName: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=100)


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    fullName: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=100)


class TeacherOut(TeacherBase):
    id: str = Field(..., description="Document ID")

    class Config:
        schema_extra = {
            "example": {
                "id": "665f8c47e4f8c1f5b8a2b7c1",
                "fullName": "Ms. Jane Doe",
                "email": "jane.doe@example.com",
                "subject": "Mathematics",
            }
        }


# Backwards compatibility alias
Teacher = TeacherOut
