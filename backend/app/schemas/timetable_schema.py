from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PeriodEntry(BaseModel):
    period: int = Field(..., ge=1, le=8, description="Period number (1-8)")
    subjectId: str = Field(..., description="Subject ObjectId string")
    teacherId: Optional[str] = Field(
        None,
        description="Teacher ObjectId string. Null when teacherAssignmentStatus='UNASSIGNED'.",
    )
    teacherAssignmentStatus: Optional[str] = Field(
        None,
        description="'ASSIGNED', 'UNASSIGNED', or 'FREE'. Required when teacherId is null.",
    )
    subjectName: Optional[str] = None
    teacherName: Optional[str] = None


class ClassScheduleSchema(BaseModel):
    Monday: List[PeriodEntry] = Field(...)
    Tuesday: List[PeriodEntry] = Field(...)
    Wednesday: List[PeriodEntry] = Field(...)
    Thursday: List[PeriodEntry] = Field(...)
    Friday: List[PeriodEntry] = Field(...)


class TimetableResponse(BaseModel):
    id: str = Field(..., description="Timetable document ID")
    generated: bool = Field(True)
    academicYear: int = Field(2026)
    createdAt: datetime
    timetable: Dict[str, ClassScheduleSchema] = Field(..., description="Weekly schedule per class (e.g. '6A')")


class TeacherPeriodEntry(BaseModel):
    period: int = Field(..., ge=1, le=8)
    class_name: str = Field(..., alias="class", description="Class name, e.g., '6A'")
    subjectId: str = Field(..., description="Subject ObjectId string")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class TeacherTimetableResponse(BaseModel):
    teacherId: str
    schedule: Dict[str, List[TeacherPeriodEntry]]


class GradeTimetableResponse(BaseModel):
    grade: int
    timetable: Dict[str, ClassScheduleSchema]


class ValidationErrorDetail(BaseModel):
    type: str = Field(..., description="Validation error type")
    message: str = Field(..., description="Human readable description of the error")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional context about the error")
