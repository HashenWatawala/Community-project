from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import logging

from app.routes import subject_routes, auth_routes
from app.database import close_client, get_database

logger = logging.getLogger("uvicorn.error")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subject_routes.router)
app.include_router(auth_routes.router)

# Background task that will keep trying to connect to MongoDB and log status
_db_monitor_task: asyncio.Task | None = None


async def _monitor_db_connection(poll_interval: int = 10):
    """Continuously try to ping the DB until successful and log the result."""
    db = get_database()
    while True:
        try:
            await db.command("ping")
            # ensure helpful index exists
            try:
                await db["subjects"].create_index("grade")
            except Exception:
                pass
            logger.info("MongoDB connected: %s", db.name)
            return
        except Exception as e:
            logger.warning("MongoDB not reachable yet: %s", e)
            await asyncio.sleep(poll_interval)

@app.get("/")
def read_root():
    return {"message": "Backend is running successfully 🚀"}

@app.on_event("startup")
async def _startup_event():
    global _db_monitor_task
    # Start background monitor that logs when DB becomes reachable
    if _db_monitor_task is None:
        _db_monitor_task = asyncio.create_task(_monitor_db_connection())


@app.on_event("shutdown")
async def _shutdown_event():
    global _db_monitor_task
    if _db_monitor_task is not None:
        _db_monitor_task.cancel()
        try:
            await _db_monitor_task
        except asyncio.CancelledError:
            pass
    # Close MongoDB client on shutdown
    await close_client()

@app.get("/health/db")
async def health_db():
    db = get_database()
    try:
        await db.command("ping")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
