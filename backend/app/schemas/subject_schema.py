from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class SubjectBase(BaseModel):
	grade: int = Field(..., ge=1, le=13, description="School grade (1-13)")
	subjectName: str = Field(..., min_length=1, max_length=100)
	periodsPerWeek: int = Field(..., ge=1, le=50)
	assignedTeacher: str = Field(..., min_length=1, max_length=100)


class SubjectCreate(SubjectBase):
	pass


class SubjectUpdate(BaseModel):
	grade: Optional[int] = Field(None, ge=1, le=13)
	subjectName: Optional[str] = Field(None, min_length=1, max_length=100)
	periodsPerWeek: Optional[int] = Field(None, ge=1, le=50)
	assignedTeacher: Optional[str] = Field(None, min_length=1, max_length=100)


class SubjectOut(SubjectBase):
	id: str = Field(..., description="Document ID")

	class Config:
		json_schema_extra = {
			"example": {
				"id": "665f8c47e4f8c1f5b8a2b7c1",
				"grade": 6,
				"subjectName": "Mathematics",
				"periodsPerWeek": 7,
				"assignedTeacher": "Ms. Jane Doe",
			}
		}


# Backwards-compatible alias used by route annotations
# The routes import `Subject` — provide that name as an alias to `SubjectOut`.
Subject = SubjectOut

