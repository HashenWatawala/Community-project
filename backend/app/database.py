from __future__ import annotations

import os
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env files if present (root and backend dirs)
load_dotenv()  # search from current working directory
# Also attempt to load backend/.env explicitly without overriding existing values
backend_env = Path(__file__).resolve().parent.parent / ".env"
if backend_env.exists():
	load_dotenv(dotenv_path=backend_env, override=False)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_mongo_uri() -> str:
	"""Get MongoDB connection string from environment, with a sensible default for local dev."""
	return os.getenv("MONGODB_URI", "mongodb://localhost:27017")


def get_db_name() -> str:
	"""Get database name from environment, default to 'community_db'."""
	return os.getenv("MONGODB_DB", "community_db")


def get_client() -> AsyncIOMotorClient:
	"""Get a singleton Motor client."""
	global _client
	if _client is None:
		_client = AsyncIOMotorClient(get_mongo_uri())
	return _client


def get_database() -> AsyncIOMotorDatabase:
	"""Return the AsyncIOMotorDatabase instance."""
	global _db
	if _db is None:
		_db = get_client()[get_db_name()]
	return _db


async def close_client() -> None:
	"""Close the Motor client on shutdown."""
	global _client
	if _client is not None:
		_client.close()
		_client = None

