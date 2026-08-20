from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database import get_database


def _collection() -> AsyncIOMotorCollection:
    db = get_database()
    return db["timetable"]


def _to_timetable_out(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "generated": doc.get("generated", True),
        "academicYear": doc.get("academicYear", 2026),
        "createdAt": doc.get("createdAt"),
        "timetable": doc.get("timetable", {}),
    }


async def get_timetable_doc() -> Optional[Dict[str, Any]]:
    col = _collection()
    doc = await col.find_one({})
    return _to_timetable_out(doc) if doc else None


async def save_timetable_doc(timetable_dict: Dict[str, Any]) -> Dict[str, Any]:
    col = _collection()
    # Delete any existing timetables to ensure only one document remains
    await col.delete_many({})
    
    doc = {
        "generated": True,
        "academicYear": 2026,
        "createdAt": datetime.utcnow(),
        "timetable": timetable_dict,
    }
    res = await col.insert_one(doc)
    doc["_id"] = res.inserted_id
    return _to_timetable_out(doc)


async def delete_timetable_doc() -> bool:
    col = _collection()
    res = await col.delete_many({})
    return res.deleted_count > 0


async def update_class_schedule(class_name: str, schedule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    col = _collection()
    doc = await col.find_one({})
    if not doc or class_name not in doc.get("timetable", {}):
        return None

    await col.update_one(
        {"_id": doc["_id"]},
        {"$set": {f"timetable.{class_name}": schedule}},
    )
    updated = await col.find_one({"_id": doc["_id"]})
    return _to_timetable_out(updated) if updated else None
