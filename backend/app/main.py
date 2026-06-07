from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Attempt to connect and ping the MongoDB cluster
    print("Connecting to MongoDB...")
    try:
        await database.client.admin.command('ping')
        print("Successfully connected to MongoDB Atlas! 🚀")
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to MongoDB: {e}")
        print("Please check your password and connection string in backend/.env\n")
    yield
    # Shutdown: Close client connection
    database.client.close()
    print("MongoDB connection closed.")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Backend is running successfully 🚀"}
