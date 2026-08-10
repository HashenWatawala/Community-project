from __future__ import annotations

from typing import Any, Optional, Union
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.timetable_schema import (
    TimetableResponse,
    TeacherTimetableResponse,
    GradeTimetableResponse,
    ClassScheduleSchema,
)
from app.services.timetable_service import (
    generate_and_save_timetable,
    get_active_timetable,
    remove_active_timetable,
    get_teacher_timetable,
    get_grade_timetable,
)

router = APIRouter(prefix="/api/timetable", tags=["timetable"])


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_timetable_endpoint():
    """
    Generates a weekly clash-free school timetable using Gemini AI and saves it to MongoDB.
    Raises 409 Conflict if a timetable already exists.
    """
    try:
        return await generate_and_save_timetable()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during timetable generation: {str(e)}"
        )


@router.get("/")
async def get_timetable_endpoint(
    teacherId: Optional[str] = Query(None, description="Get dynamically computed schedule for a specific teacher"),
    grade: Optional[int] = Query(None, ge=6, le=11, description="Get dynamically filtered schedule for a grade (6-11)"),
    class_name: Optional[str] = Query(None, alias="className", description="Get schedule for a specific class (e.g. '6A')")
) -> Any:
    """
    Retrieves the timetable. Can filter dynamically by teacher, grade, or class name.
    If no timetable has been generated, returns 404.
    """
    # 1. Filter by teacherId
    if teacherId is not None:
        teacher_schedule = await get_teacher_timetable(teacherId)
        if not teacher_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No timetable found or no schedule matches teacher ID: {teacherId}"
            )
        return teacher_schedule

    # 2. Filter by grade
    if grade is not None:
        grade_schedule = await get_grade_timetable(grade)
        if not grade_schedule or not grade_schedule["timetable"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No timetable found or no classes match grade: {grade}"
            )
        return grade_schedule

    # 3. Filter by class_name
    if class_name is not None:
        timetable_doc = await get_active_timetable()
        if not timetable_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No timetable has been generated yet."
            )
        class_schedule = timetable_doc.get("timetable", {}).get(class_name)
        if not class_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No schedule found for class: {class_name}"
            )
        return class_schedule

    # 4. Return the full timetable
    timetable_doc = await get_active_timetable()
    if not timetable_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No timetable has been generated yet."
        )
    return timetable_doc


@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_timetable_endpoint():
    """
    Deletes the currently saved timetable document from MongoDB.
    """
    deleted = await remove_active_timetable()
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No timetable exists to delete."
        )
    return {"message": "Timetable deleted successfully."}
