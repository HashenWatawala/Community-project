from __future__ import annotations

from typing import List, Any, Optional

from fastapi import APIRouter, HTTPException, status

from app.schemas.teacher_schema import TeacherCreate, TeacherOut, TeacherUpdate
from app.models.teacher_model import (
	list_teachers,
	get_teacher,
	create_teacher,
	update_teacher,
	delete_teacher,
)

router = APIRouter(prefix="/api/teachers", tags=["teachers"])


@router.get("/", response_model=List[TeacherOut])
async def get_all_teachers():
	return await list_teachers()


@router.get("/{teacher_id}", response_model=TeacherOut)
async def get_teacher_by_id(teacher_id: str):
	teacher = await get_teacher(teacher_id)
	if not teacher:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
	return teacher


@router.post("/", response_model=TeacherOut, status_code=status.HTTP_201_CREATED)
async def create_teacher_endpoint(payload: TeacherCreate):
	return await create_teacher(payload.model_dump())


@router.put("/{teacher_id}", response_model=TeacherOut)
async def update_teacher_endpoint(teacher_id: str, payload: TeacherUpdate):
	updates = {k: v for k, v in payload.model_dump().items() if v is not None}
	if not updates:
		existing = await get_teacher(teacher_id)
		if not existing:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
		return existing
	updated = await update_teacher(teacher_id, updates)
	if not updated:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
	return updated


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher_endpoint(teacher_id: str):
	ok = await delete_teacher(teacher_id)
	if not ok:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
	return None
