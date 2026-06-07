import motor.motor_asyncio
from app.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DETAILS)
database = client[settings.DATABASE_NAME]
