from __future__ import annotations

from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database import get_database


def _collection() -> AsyncIOMotorCollection:
	db = get_database()
	return db["subjects"]


def _to_subject_out(doc: Dict[str, Any]) -> Dict[str, Any]:
	return {
		"id": str(doc.get("_id")),
		"grade": doc.get("grade"),
		"subjectName": doc.get("subjectName"),
		"periodsPerWeek": doc.get("periodsPerWeek"),
		"assignedTeacher": doc.get("assignedTeacher"),
	}


async def create_subject(data: Dict[str, Any]) -> Dict[str, Any]:
	col = _collection()
	res = await col.insert_one(data)
	inserted = await col.find_one({"_id": res.inserted_id})
	assert inserted is not None
	return _to_subject_out(inserted)


async def list_subjects() -> List[Dict[str, Any]]:
	col = _collection()
	cursor = col.find({}, {"_id": 1, "grade": 1, "subjectName": 1, "periodsPerWeek": 1, "assignedTeacher": 1})
	return [_to_subject_out(doc) async for doc in cursor]


async def list_subjects_by_grade(grade: int) -> List[Dict[str, Any]]:
	col = _collection()
	cursor = col.find({"grade": grade})
	return [_to_subject_out(doc) async for doc in cursor]


async def get_subject(subject_id: str) -> Optional[Dict[str, Any]]:
	col = _collection()
	try:
		oid = ObjectId(subject_id)
	except Exception:
		return None
	doc = await col.find_one({"_id": oid})
	return _to_subject_out(doc) if doc else None


async def update_subject(subject_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
	col = _collection()
	try:
		oid = ObjectId(subject_id)
	except Exception:
		return None
	await col.update_one({"_id": oid}, {"$set": updates})
	updated = await col.find_one({"_id": oid})
	return _to_subject_out(updated) if updated else None


async def delete_subject(subject_id: str) -> bool:
	col = _collection()
	try:
		oid = ObjectId(subject_id)
	except Exception:
		return False
	res = await col.delete_one({"_id": oid})
	return res.deleted_count == 1

