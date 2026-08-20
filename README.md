# Kudapaduwa Timetable Management System (TMS)

A modern timetable management project with a **FastAPI** backend and a **React + Vite** frontend.

## Project Structure

- `backend/` — FastAPI backend application, database models, routes, and services.
- `frontend/` — React UI application built with Vite.
- `.env.example` — Backend environment variable template.

---

## Prerequisites

- Python 3.11+ (or compatible Python 3)
- Node.js 18+ and npm
- MongoDB instance (local or Atlas)

---

## Backend Setup

1. Open a terminal and navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:

   ```bash
   python -m venv venv
   ```

   - Windows PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - macOS / Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install backend dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create the environment file from the example:

   ```bash
   # Linux / macOS
   cp .env.example .env

   # Windows PowerShell
   Copy-Item .env.example .env
   ```

5. Open `backend/.env` and configure your values.

6. Start the backend server:

   ```bash
   uvicorn app.main:app --reload
   ```

7. Verify the backend is running at:

   - `http://127.0.0.1:8000`
   - OpenAPI docs: `http://127.0.0.1:8000/docs`

---

## Frontend Setup

1. Open a new terminal and navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install frontend dependencies:

   ```bash
   npm install
   ```

3. Start the frontend development server:

   ```bash
   npm run dev
   ```

4. Open the application in your browser at:

   - `http://127.0.0.1:5173`

---

## Backend Environment Variables

The backend uses the following variables in `backend/.env`:

- `MONGODB_URI` — MongoDB connection URI
- `MONGODB_DB` — MongoDB database name
- `SECRET_KEY` — JWT signing secret
- `JWT_ALGORITHM` — JWT algorithm (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` — Token expiry in minutes
- `GEMINI_API_KEY` — Optional Gemini API key if used

---

## Seed Sample Data

Populate the database with example teachers and subjects:

```bash
cd backend
python seed_sample_data.py
```

---

## Health Check

Verify backend and MongoDB connectivity:

```bash
curl http://127.0.0.1:8000/health/db
```

Expected response:

```json
{ "status": "ok" }
```

---

## Build a Windows Executable

The release build packages the FastAPI backend and the compiled React frontend into one file. Build it on Windows from the project root:

```powershell
cd frontend
npm install
npm run build
cd ..
& .\backend\venv\Scripts\pip.exe install -r .\backend\requirements.txt
& .\backend\venv\Scripts\pip.exe install pyinstaller
& .\backend\venv\Scripts\pyinstaller.exe --clean --noconfirm .\TimetableManagementSystem.spec
```

The executable is created at `dist\TimetableManagementSystem.exe`. Copy `.env.example` to `dist\.env`, replace the placeholders with the target MongoDB and API settings, and then run the executable. MongoDB must be reachable from the target computer; it is not bundled into the executable.

Close any running copy of `TimetableManagementSystem.exe` before rebuilding, otherwise Windows may keep the old executable because the file is locked.

## Notes

- Ensure MongoDB is running before starting the backend.
- Keep `backend/.env` out of source control.
- If frontend or backend port settings change, update CORS origins in `backend/app/main.py`.
