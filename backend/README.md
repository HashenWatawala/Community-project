# Backend (FastAPI)

FastAPI backend for Subject Management with MongoDB (Motor).

## Quick start

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```powershell
pip install -r backend/requirements.txt
```

3. Configure environment variables:

- Copy `backend/.env.example` to `backend/.env` and adjust values.

4. Run the server:

```powershell
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

The API will be available at http://127.0.0.1:8000

CORS is enabled for Vite dev origins (5173, 5174).

### Health check

Verify MongoDB connectivity:

```
GET http://127.0.0.1:8000/health/db
```

## Endpoints

- `GET /api/subjects/` – List all subjects
- `GET /api/subjects/grade/{grade}` – List subjects for a grade
- `GET /api/subjects/{id}` – Get a subject by id
- `POST /api/subjects/` – Create new subject
- `PUT /api/subjects/{id}` – Update a subject
- `DELETE /api/subjects/{id}` – Delete a subject

## Data model

```json
{
  "id": "string",
  "grade": 6,
  "subjectName": "Mathematics",
  "periodsPerWeek": 7,
  "assignedTeacher": "Ms. Jane Doe"
}
```
