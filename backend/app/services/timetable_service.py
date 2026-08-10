from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from app.models.timetable_model import (
    get_timetable_doc,
    save_timetable_doc,
    delete_timetable_doc,
)
from app.models.subject_model import list_subjects
from app.models.teacher_model import list_teachers
from app.services.gemini_service import generate_timetable_from_ai
from app.services.timetable_validator import validate_timetable

logger = logging.getLogger("uvicorn.error")

# Max retries if AI output fails validation
_MAX_RETRIES = 5


async def generate_and_save_timetable() -> Dict[str, Any]:
    """
    Full orchestration pipeline:
    1. Reject if a timetable already exists (HTTP 409).
    2. Pre-load teacher & subject data for validation.
    3. Call Gemini AI (retries up to _MAX_RETRIES on validation failure).
    4. Save and return the validated timetable.
    """
    # ── Guard: one timetable at a time ───────────────────────────────────────
    existing = await get_timetable_doc()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A timetable already exists. "
                "Delete it first before generating a new one."
            ),
        )

    # ── Pre-load reference data ───────────────────────────────────────────────
    teachers = await list_teachers()
    subjects = await list_subjects()

    if not teachers:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No teachers found. Add teacher records before generating a timetable.",
        )
    if not subjects:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No subjects found. Add subject records before generating a timetable.",
        )

    # ── Retry loop ────────────────────────────────────────────────────────────
    last_errors: list = []

    for attempt in range(1, _MAX_RETRIES + 1):
        logger.info("Timetable generation attempt %d / %d …", attempt, _MAX_RETRIES)

        try:
            raw_timetable = await generate_timetable_from_ai(teachers, subjects)
        except ValueError as exc:
            # ValueError contains diagnostic info (pre-flight failures, solver
            # exhaustion details).  Surface it directly so the user can act.
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )
        except Exception as exc:
            logger.exception("Unexpected error during timetable generation attempt %d", attempt)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Timetable generation error: {exc}",
            )

        # ── Validate ──────────────────────────────────────────────────────────
        val = validate_timetable(raw_timetable, subjects, teachers)
        if val["is_valid"]:
            logger.info("Timetable passed validation on attempt %d.", attempt)
            return await save_timetable_doc(raw_timetable)

        last_errors = val["errors"]
        logger.warning(
            "Attempt %d: validation failed with %d error(s). %s",
            attempt,
            len(last_errors),
            "Retrying…" if attempt < _MAX_RETRIES else "No retries left.",
        )

    # ── All retries exhausted ─────────────────────────────────────────────────
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "message": (
                f"Timetable violated constraints after {_MAX_RETRIES} generation attempts. "
                "Verify that all subjects reference valid teacher ObjectIds and "
                "that period counts sum to 40 per grade."
            ),
            "errors": last_errors[:50],
        },
    )


async def get_active_timetable() -> Optional[Dict[str, Any]]:
    """Returns the current stored timetable document, or None."""
    return await get_timetable_doc()


async def remove_active_timetable() -> bool:
    """Deletes the current timetable. Returns True if a document was deleted."""
    return await delete_timetable_doc()


async def get_teacher_timetable(teacher_id: str) -> Optional[Dict[str, Any]]:
    """
    Dynamically builds a teacher's schedule from the stored class timetables.
    """
    doc = await get_timetable_doc()
    if not doc:
        return None

    norm_id = str(teacher_id).strip()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    schedule: Dict[str, list] = {day: [] for day in days}

    for class_name, days_schedule in doc.get("timetable", {}).items():
        for day in days:
            for entry in days_schedule.get(day, []):
                if str(entry.get("teacherId", "")).strip() == norm_id:
                    schedule[day].append({
                        "period": entry["period"],
                        "class": class_name,
                        "subjectId": entry["subjectId"],
                    })

    for day in days:
        schedule[day].sort(key=lambda x: x["period"])

    return {"teacherId": teacher_id, "schedule": schedule}


async def get_grade_timetable(grade: int) -> Optional[Dict[str, Any]]:
    """
    Extracts timetable entries for all classes in a given grade.
    """
    doc = await get_timetable_doc()
    if not doc:
        return None

    grade_timetable: Dict[str, Any] = {}
    for class_name, schedule in doc.get("timetable", {}).items():
        try:
            if int(class_name[:-1]) == grade:
                grade_timetable[class_name] = schedule
        except ValueError:
            continue

    return {"grade": grade, "timetable": grade_timetable}
