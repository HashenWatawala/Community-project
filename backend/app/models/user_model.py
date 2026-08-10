from __future__ import annotations

from typing import Optional
from bson import ObjectId
from app.database import get_database


async def get_user_by_username(username: str) -> Optional[dict]:
    db = get_database()
    user = await db["users"].find_one({"username": username})
    if user:
        user["id"] = str(user.pop("_id"))
    return user


async def get_user_by_email(email: str) -> Optional[dict]:
    db = get_database()
    user = await db["users"].find_one({"email": email})
    if user:
        user["id"] = str(user.pop("_id"))
    return user


async def create_user(data: dict) -> dict:
    db = get_database()
    res = await db["users"].insert_one(data)
    user = await db["users"].find_one({"_id": res.inserted_id})
    user["id"] = str(user.pop("_id"))
    return user


async def get_user(user_id: str) -> Optional[dict]:
    db = get_database()
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user.pop("_id"))
    return user
