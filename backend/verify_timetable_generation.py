import asyncio

from app.services.timetable_service import generate_and_save_timetable


async def main() -> None:
    result = await generate_and_save_timetable()
    print("Generated timetable:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
