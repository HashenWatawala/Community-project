# Kudapaduwa Timetable Management System (TMS)

A comprehensive and modern web application designed to streamline the scheduling and management of classes, grades, subjects, rooms, and teachers. 

This repository is split into a **FastAPI** backend and a **React + Vite** frontend.

---

## ⚙️ Environment Variables Configuration

The backend application requires configuration settings loaded from an environment file (`.env`). A template file is provided at `backend/.env.example` to guide your setup.

### 1. Setup Environment File
Create a `.env` file in the `backend/` directory by copying the example template:
```bash
cp backend/.env.example backend/.env
```

### 2. Available Variables

Configure the following variables in your `backend/.env` file:

| Environment Variable | Description | Default / Example Value |
| :--- | :--- | :--- |
| `MONGO_DETAILS` | The connection URI to the MongoDB database (supports local connection or MongoDB Atlas). | `mongodb+srv://<username>:<password>@cluster.mongodb.net/?...` or `mongodb://localhost:27017` |
| `DATABASE_NAME` | The target database name for storing collections. | `tms_db` |
| `SECRET_KEY` | A strong cryptographic secret key used for signing and validating JWT tokens for user authentication. | *Change this to a long random security string in production* |

> [!WARNING]
> Never commit the `.env` file containing production credentials or secrets to git. The `.gitignore` has been updated to ignore this file.

---

## 🚀 Getting Started

### Backend Setup (FastAPI)

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend API will be available at `http://127.0.0.1:8000`. You can access interactive documentation at `http://127.0.0.1:8000/docs`.

### Frontend Setup (React + Vite)

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```
   The frontend will be active at `http://localhost:5173`.

---

## 🔒 Security & Version Control
To protect sensitive credentials (like MongoDB connection strings and JWT signing keys), the environment configuration file `.env` is excluded from git tracking. A root-level `.gitignore` ensures that:
- Node modules are ignored.
- The Python virtual environment (`venv/`) is ignored.
- The `.env` file containing actual secrets is ignored.
- Automatically generated Python/JS cache files are ignored.
