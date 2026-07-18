import asyncio

from app.database import get_database


async def main() -> None:
    db = get_database()
    deleted = await db["timetable"].delete_many({})
    print(f"Cleared {deleted.deleted_count} timetable document(s).")


if __name__ == "__main__":
    asyncio.run(main())
