from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, status

from app.schemas.subject_schema import SubjectCreate, Subject, SubjectUpdate
from app.models.subject_model import (
	create_subject,
	delete_subject,
	get_subject,
	list_subjects,
	list_subjects_by_grade,
	update_subject,
)

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("/", response_model=List[Subject])
async def get_all_subjects():
	return await list_subjects()


@router.get("/grade/{grade}", response_model=List[Subject])
async def get_subjects_for_grade(grade: int):
	return await list_subjects_by_grade(grade)


@router.get("/{subject_id}", response_model=Subject)
async def get_subject_by_id(subject_id: str):
	subject = await get_subject(subject_id)
	if not subject:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
	return subject


@router.post("/", response_model=Subject, status_code=status.HTTP_201_CREATED)
async def create_subject_endpoint(payload: SubjectCreate):
	return await create_subject(payload.model_dump())


@router.put("/{subject_id}", response_model=Subject)
async def update_subject_endpoint(subject_id: str, payload: SubjectUpdate):
	updates = {k: v for k, v in payload.model_dump().items() if v is not None}
	if not updates:
		existing = await get_subject(subject_id)
		if not existing:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
		return existing
	updated = await update_subject(subject_id, updates)
	if not updated:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
	return updated


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject_endpoint(subject_id: str):
	ok = await delete_subject(subject_id)
	if not ok:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
	return None

