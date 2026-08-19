import asyncio
import logging
from contextlib import asynccontextmanager

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import get_database, close_client
from app.routes import subject_routes, auth_routes, teacher_routes, timetable_routes

logger = logging.getLogger("uvicorn.error")

# ---- Lifespan (startup / shutdown) ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to MongoDB...")
    try:
        db = get_database()
        await db.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to MongoDB: {e}")
        print("Please check your password and connection string in backend/.env\n")
    yield
    await close_client()
    print("MongoDB connection closed.")

app = FastAPI(lifespan=lifespan)

# ---- Root endpoint ----
@app.get("/health")
def read_health():
    return {"status": "ok", "message": "Backend is running successfully 🚀"}

# ---- CORS middleware ----
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

# ---- Include routers ----
app.include_router(subject_routes.router)
app.include_router(auth_routes.router)
app.include_router(teacher_routes.router)
app.include_router(timetable_routes.router)

# ---- Background DB monitor task ----
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

@app.on_event("startup")
async def _startup_event():
    global _db_monitor_task
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
    # client already closed via lifespan

# ---- Health endpoint ----
@app.get("/health/db")
async def health_db():
    db = get_database()
    try:
        await db.command("ping")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- Serve React Frontend ----
# Determine base directory depending on whether we're frozen (PyInstaller) or running from source
if getattr(sys, 'frozen', False):
    base_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    frontend_dist_dir = base_dir / "frontend" / "dist"
else:
    base_dir = Path(__file__).resolve().parent.parent.parent
    frontend_dist_dir = base_dir / "frontend" / "dist"

if frontend_dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist_dir / "assets")), name="assets")

    # Catch-all route for SPA client-side routing
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        
        index_file = frontend_dist_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"error": "Frontend build not found"}
else:
    logger.warning(f"Frontend dist directory not found at {frontend_dist_dir}")