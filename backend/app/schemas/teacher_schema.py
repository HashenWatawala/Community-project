from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class SubjectAssignment(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    grades: List[int] = Field(default_factory=list)


class TeacherBase(BaseModel):
    fullName: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    nicNo: Optional[str] = Field(None, min_length=5, max_length=20)
    contactNumber: Optional[str] = Field(None, min_length=7, max_length=20)
    hasAssignClass: bool = Field(False)
    subjects: List[SubjectAssignment] = Field(default_factory=list)


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    fullName: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    nicNo: Optional[str] = Field(None, min_length=5, max_length=20)
    contactNumber: Optional[str] = Field(None, min_length=7, max_length=20)
    hasAssignClass: Optional[bool] = None
    subjects: Optional[List[SubjectAssignment]] = None


class TeacherOut(TeacherBase):
    id: str = Field(..., description="Document ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "665f8c47e4f8c1f5b8a2b7c1",
                "fullName": "Ms. Jane Doe",
                "email": "jane.doe@example.com",
                "nicNo": "198765432V",
                "contactNumber": "+94771234567",
                "hasAssignClass": True,
                "subjects": [
                    {"name": "Mathematics", "grades": [6, 7, 8]},
                ],
            }
        }


# Backwards compatibility alias
Teacher = TeacherOut

