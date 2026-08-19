from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

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
    3. Call the deterministic solver / Gemini AI fallback.
    4. Validate — retrying on hard errors only.
       A timetable that has ONLY "unassigned_teacher" warnings (no hard errors)
       is accepted and saved immediately without retrying.
    5. Save and return the validated timetable along with any unassigned diagnostics.
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
            result = await generate_timetable_from_ai(teachers, subjects)
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

        # ── Unpack result envelope ────────────────────────────────────────────
        # The solver returns {"timetable": {...}, "unassigned_diagnostics": [...]}
        # The Gemini fallback returns the same envelope shape.
        # Legacy callers that return a bare dict are also handled here.
        if isinstance(result, dict) and "timetable" in result:
            raw_timetable = result["timetable"]
            unassigned_diagnostics: List[Dict[str, Any]] = result.get("unassigned_diagnostics", [])
        else:
            # Bare timetable dict (legacy / unexpected shape)
            raw_timetable = result
            unassigned_diagnostics = []

        # ── Validate ──────────────────────────────────────────────────────────
        # Pass the timetable dict to the validator (it also understands the envelope).
        val = validate_timetable(result, subjects, teachers)

        if val["is_valid"]:
            logger.info("Timetable passed validation on attempt %d.", attempt)
            saved = await save_timetable_doc(raw_timetable)

            # Include unassigned diagnostics in the response so the frontend /
            # API consumers can surface them to administrators.
            response = dict(saved)
            if unassigned_diagnostics:
                response["unassigned_diagnostics"] = unassigned_diagnostics
                response["has_unassigned_teachers"] = True
                logger.warning(
                    "Saved timetable has %d slot(s) with no teacher assigned.",
                    len(unassigned_diagnostics),
                )
            else:
                response["unassigned_diagnostics"] = []
                response["has_unassigned_teachers"] = False

            return response

        # ── Only hard errors trigger a retry ──────────────────────────────────
        # Timetables with ONLY "unassigned_teacher" warnings (and no hard errors)
        # are accepted above (val["is_valid"] will be True in that case).
        # We only reach here when there are genuine hard errors.
        last_errors = val["errors"]
        hard_error_count = len(val["hard_errors"])
        logger.warning(
            "Attempt %d: validation failed with %d hard error(s). %s",
            attempt,
            hard_error_count,
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
    Only includes periods where this teacher is explicitly assigned (skips UNASSIGNED slots).
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
                # Only include entries where this teacher is actually assigned
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
