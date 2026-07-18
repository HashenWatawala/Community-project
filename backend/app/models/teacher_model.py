from __future__ import annotations

from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database import get_database


def _collection() -> AsyncIOMotorCollection:
    db = get_database()
    return db["teachers"]


def _to_teacher_out(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "fullName": doc.get("fullName"),
        "email": doc.get("email"),
        "nicNo": doc.get("nicNo"),
        "contactNumber": doc.get("contactNumber"),
        "hasAssignClass": doc.get("hasAssignClass", False),
        "subjects": doc.get("subjects", []),
    }


async def create_teacher(data: Dict[str, Any]) -> Dict[str, Any]:
    col = _collection()
    res = await col.insert_one(data)
    inserted = await col.find_one({"_id": res.inserted_id})
    assert inserted is not None
    return _to_teacher_out(inserted)


async def list_teachers() -> List[Dict[str, Any]]:
    col = _collection()
    cursor = col.find(
        {},
        {
            "_id": 1,
            "fullName": 1,
            "email": 1,
            "nicNo": 1,
            "contactNumber": 1,
            "hasAssignClass": 1,
            "subjects": 1,
        },
    )
    return [_to_teacher_out(doc) async for doc in cursor]


async def get_teacher(teacher_id: str) -> Optional[Dict[str, Any]]:
    col = _collection()
    try:
        oid = ObjectId(teacher_id)
    except Exception:
        return None
    doc = await col.find_one({"_id": oid})
    return _to_teacher_out(doc) if doc else None


async def update_teacher(teacher_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    col = _collection()
    try:
        oid = ObjectId(teacher_id)
    except Exception:
        return None
    await col.update_one({"_id": oid}, {"$set": updates})
    updated = await col.find_one({"_id": oid})
    return _to_teacher_out(updated) if updated else None


async def delete_teacher(teacher_id: str) -> bool:
    col = _collection()
    try:
        oid = ObjectId(teacher_id)
    except Exception:
        return False
    res = await col.delete_one({"_id": oid})
    return res.deleted_count == 1

