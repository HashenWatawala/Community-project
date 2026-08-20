from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

# Status constants — must match gemini_service.py
_TEACHER_UNASSIGNED_STATUS = "UNASSIGNED"
_FREE_PERIOD_SUBJECT_ID = "__free_period__"
_FREE_PERIOD_TEACHER_ID = "__none__"


def _normalize_subject_name(value: Any) -> str:
    return str(value).strip().lower()


def _normalize_id(value: Any) -> str:
    return str(value).strip()


def validate_timetable(
    timetable_data: Dict[str, Any],
    subjects: List[Dict[str, Any]],
    teachers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Validates the generated timetable against all schedule constraints.

    Constraints checked:
    1. Teacher Clashes  — a teacher may not teach >1 class at the same day+period.
    2. Period Clashes   — each class may have only one subject per period per day.
    3. Subject Count    — scheduled count must equal periodsPerWeek from MongoDB.
    4. Teacher Assignment — only the assigned teacher may teach a subject (skipped
                            for entries explicitly marked UNASSIGNED).
    5. Missing Periods  — each class must have all 8 periods on every weekday.
    6. Grade Subject Match — a class may only use subjects belonging to its grade.

    Teacher-unassigned entries (teacherId=null, teacherAssignmentStatus="UNASSIGNED"):
    - Are VALID as long as subjectId is present and valid.
    - Are NEVER treated as incomplete or blank.
    - Skip teacher qualification, clash, and load checks.
    - Generate informational warnings, not hard errors.

    Returns:
        {"is_valid": bool, "errors": List[Dict[str, Any]], "hard_errors": ..., "warnings": ...}
    """
    hard_errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    # ── Lookups ──────────────────────────────────────────────────────────────
    # Normalise IDs to stripped lowercase strings for robust comparison
    subject_lookup: Dict[str, Dict[str, Any]] = {
        str(s["id"]).strip(): s for s in subjects
    }
    teacher_lookup: Dict[str, Dict[str, Any]] = {
        str(t["id"]).strip(): t for t in teachers
    }

    expected_classes = ["6A", "7A", "8A", "9A", "10A", "11A"]
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    # Support timetable wrapped in {"timetable": {...}} envelope (solver output)
    # or a bare dict (legacy / Gemini fallback).
    if "timetable" in timetable_data and isinstance(timetable_data["timetable"], dict):
        raw_schedule = timetable_data["timetable"]
    else:
        raw_schedule = timetable_data

    # ── Check that all expected classes are present ───────────────────────────
    for cls in expected_classes:
        if cls not in raw_schedule:
            hard_errors.append({
                "type": "missing_class",
                "message": f"Class {cls} is missing from the generated timetable.",
                "details": {"class": cls},
            })

    active_classes = [c for c in expected_classes if c in raw_schedule]

    # ── Per-day teacher occupancy: day → period → teacher_id → [classes] ──────
    teacher_schedule: Dict[str, Dict[int, Dict[str, List[str]]]] = {
        day: {p: {} for p in range(1, 9)} for day in days_of_week
    }

    # ── Per-teacher weekly load counts: teacher_id → periods scheduled ────────
    teacher_weekly_load: Dict[str, int] = {str(t['id']).strip(): 0 for t in teachers}

    # ── Per-class subject counters: class → subject_id → count ───────────────
    subject_counts: Dict[str, Dict[str, int]] = {cls: {} for cls in active_classes}

    for class_name in active_classes:
        # Extract numeric grade from class name (e.g. "6A" → 6, "10A" → 10)
        try:
            class_grade = int(class_name[:-1])
        except ValueError:
            hard_errors.append({
                "type": "invalid_class_name",
                "message": f"Cannot parse grade from class name: {class_name}",
                "details": {"class": class_name},
            })
            continue

        class_schedule = raw_schedule[class_name]

        for day in days_of_week:
            # ── Day presence ──────────────────────────────────────────────────
            if day not in class_schedule:
                hard_errors.append({
                    "type": "missing_day",
                    "message": f"Day '{day}' missing in schedule for class {class_name}.",
                    "details": {"class": class_name, "day": day},
                })
                continue

            periods_list = class_schedule[day]
            if not isinstance(periods_list, list):
                hard_errors.append({
                    "type": "invalid_day_format",
                    "message": f"Schedule for {class_name}/{day} must be a list.",
                    "details": {"class": class_name, "day": day},
                })
                continue

            seen_periods: set = set()

            for entry in periods_list:
                if not isinstance(entry, dict):
                    hard_errors.append({
                        "type": "invalid_period_format",
                        "message": f"Period entry in {class_name}/{day} must be an object.",
                        "details": {"class": class_name, "day": day},
                    })
                    continue

                p_num = entry.get("period")
                raw_sub_id = entry.get("subjectId", "")
                raw_teach_id = entry.get("teacherId")  # may legitimately be None
                assignment_status = str(entry.get("teacherAssignmentStatus", "")).upper()

                # Normalise subject ID
                sub_id = str(raw_sub_id).strip() if raw_sub_id is not None else ""

                # Determine if this entry is an explicit UNASSIGNED entry
                is_unassigned = (
                    (raw_teach_id is None or str(raw_teach_id).strip() == "")
                    and assignment_status == _TEACHER_UNASSIGNED_STATUS
                )

                # Normalise teacher ID only when a teacher is actually present
                teach_id: str = ""
                if not is_unassigned and raw_teach_id is not None:
                    teach_id = str(raw_teach_id).strip()

                # ── Required fields ────────────────────────────────────────────
                # subjectId must always be present.
                # teacherId may be null ONLY when teacherAssignmentStatus == "UNASSIGNED".
                # If teacherId is null/empty and status is NOT "UNASSIGNED" → hard error.
                if p_num is None or not sub_id:
                    hard_errors.append({
                        "type": "incomplete_period_entry",
                        "message": (
                            f"Incomplete period entry in {class_name}/{day}. "
                            "Must contain period and subjectId."
                        ),
                        "details": {"class": class_name, "day": day, "entry": entry},
                    })
                    continue

                if (raw_teach_id is None or str(raw_teach_id).strip() == "") and not is_unassigned:
                    hard_errors.append({
                        "type": "incomplete_period_entry",
                        "message": (
                            f"Period {p_num} in {class_name}/{day} has no teacherId and "
                            "teacherAssignmentStatus is not 'UNASSIGNED'. "
                            "Set teacherAssignmentStatus='UNASSIGNED' when teacherId is null."
                        ),
                        "details": {"class": class_name, "day": day, "entry": entry},
                    })
                    continue

                # ── Period range ────────────────────────────────────────────────
                if not isinstance(p_num, int) or p_num < 1 or p_num > 8:
                    hard_errors.append({
                        "type": "invalid_period_number",
                        "message": f"Period {p_num} in {class_name}/{day} is out of range (1–8).",
                        "details": {"class": class_name, "day": day, "period": p_num},
                    })
                    continue

                # ── Duplicate period (period clash within class) ────────────────
                if p_num in seen_periods:
                    hard_errors.append({
                        "type": "period_clash",
                        "message": f"Period {p_num} appears more than once for {class_name}/{day}.",
                        "details": {"class": class_name, "day": day, "period": p_num},
                    })
                seen_periods.add(p_num)

                # ── Subject exists in DB ────────────────────────────────────────
                subject = subject_lookup.get(sub_id)
                if not subject:
                    hard_errors.append({
                        "type": "invalid_subject",
                        "message": (
                            f"Subject ID '{sub_id}' in {class_name}/{day} P{p_num} "
                            "was not found in the subjects collection."
                        ),
                        "details": {
                            "class": class_name, "day": day,
                            "period": p_num, "subjectId": sub_id,
                        },
                    })
                    continue

                # ── Grade subject match ─────────────────────────────────────────
                if subject["grade"] != class_grade:
                    hard_errors.append({
                        "type": "grade_subject_mismatch",
                        "message": (
                            f"Subject '{subject['subjectName']}' (Grade {subject['grade']}) "
                            f"is scheduled in {class_name} (Grade {class_grade}) on {day} P{p_num}."
                        ),
                        "details": {
                            "class": class_name, "day": day, "period": p_num,
                            "subjectId": sub_id, "subjectName": subject["subjectName"],
                            "subjectGrade": subject["grade"], "classGrade": class_grade,
                        },
                    })

                # ── UNASSIGNED entry: emit warning, skip all teacher checks ──────
                if is_unassigned:
                    warnings.append({
                        "type": "unassigned_teacher",
                        "message": (
                            f"{class_name}/{day} P{p_num}: '{subject['subjectName']}' "
                            "has no teacher assigned (teacherAssignmentStatus=UNASSIGNED)."
                        ),
                        "details": {
                            "class": class_name, "day": day, "period": p_num,
                            "subjectId": sub_id, "subjectName": subject["subjectName"],
                        },
                    })
                    # Count the subject period (it still contributes to the 40-period total)
                    subject_counts[class_name][sub_id] = (
                        subject_counts[class_name].get(sub_id, 0) + 1
                    )
                    # Do NOT track teacher occupancy or load — no teacher assigned
                    continue

                # ── Teacher assignment (only for normally assigned entries) ───────
                expected_teach_id = _normalize_id(subject.get("assignedTeacher", ""))
                qualified_teachers: List[str] = []
                if expected_teach_id:
                    qualified_teachers.append(expected_teach_id)

                for teacher in teachers:
                    teacher_id = _normalize_id(teacher.get("id", ""))
                    if not teacher_id:
                        continue
                    for t_subject in teacher.get("subjects", []):
                        if _normalize_subject_name(t_subject.get("name", "")) == _normalize_subject_name(subject.get("subjectName", "")):
                            grades = t_subject.get("grades") or []
                            if class_grade in grades:
                                if teacher_id not in qualified_teachers:
                                    qualified_teachers.append(teacher_id)

                if teach_id not in qualified_teachers:
                    actual_name = teacher_lookup.get(teach_id, {}).get("fullName", teach_id)
                    expected_name = None
                    if expected_teach_id and expected_teach_id in teacher_lookup:
                        expected_name = teacher_lookup[expected_teach_id]["fullName"]
                    if expected_name:
                        message = (
                            f"Teacher '{actual_name}' is not qualified for '{subject['subjectName']}' in {class_name}/{day} P{p_num}. "
                            f"Expected '{expected_name}' or another qualified teacher."
                        )
                    else:
                        message = (
                            f"Teacher '{actual_name}' is not qualified for '{subject['subjectName']}' in {class_name}/{day} P{p_num}."
                        )
                    hard_errors.append({
                        "type": "invalid_teacher_assignment",
                        "message": message,
                        "details": {
                            "class": class_name, "day": day, "period": p_num,
                            "subjectId": sub_id,
                            "expectedTeacherId": expected_teach_id,
                            "actualTeacherId": teach_id,
                        },
                    })

                # ── Track subject count ────────────────────────────────────────
                subject_counts[class_name][sub_id] = (
                    subject_counts[class_name].get(sub_id, 0) + 1
                )

                # ── Track teacher occupancy for clash check ────────────────────
                slot = teacher_schedule[day][p_num]
                if teach_id not in slot:
                    slot[teach_id] = []
                slot[teach_id].append(class_name)
                teacher_weekly_load[teach_id] = teacher_weekly_load.get(teach_id, 0) + 1

            # ── Missing periods for this class/day (informational warning) ──────
            missing = [p for p in range(1, 9) if p not in seen_periods]
            if missing:
                warnings.append({
                    "type": "missing_periods",
                    "message": f"{class_name}/{day} has unassigned (blank) periods: {missing}.",
                    "details": {
                        "class": class_name, "day": day,
                        "missing_periods": missing,
                    },
                })

    # ── Cross-class teacher clash check ──────────────────────────────────────
    for day in days_of_week:
        for p_num in range(1, 9):
            for t_id, classes in teacher_schedule[day][p_num].items():
                if len(classes) > 1:
                    teacher = teacher_lookup.get(t_id)
                    teacher_name = teacher["fullName"] if teacher else t_id
                    hard_errors.append({
                        "type": "teacher_clash",
                        "message": (
                            f"Teacher '{teacher_name}' is scheduled in multiple classes "
                            f"on {day} Period {p_num}: {classes}."
                        ),
                        "details": {
                            "day": day, "period": p_num,
                            "teacherId": t_id, "teacherName": teacher_name,
                            "classes": classes,
                        },
                    })

    # ── Weekly subject count check (informational warning) ────────────────────
    for class_name in active_classes:
        class_grade = int(class_name[:-1])
        grade_subjects = [s for s in subjects if s["grade"] == class_grade]

        for subject in grade_subjects:
            sub_id = str(subject["id"]).strip()
            expected = subject["periodsPerWeek"]
            actual = subject_counts[class_name].get(sub_id, 0)

            if actual != expected:
                warnings.append({
                    "type": "subject_count_mismatch",
                    "message": (
                        f"'{subject['subjectName']}' in {class_name}: "
                        f"scheduled {actual} times (requested {expected} periods/week)."
                    ),
                    "details": {
                        "class": class_name,
                        "subjectId": sub_id,
                        "subjectName": subject["subjectName"],
                        "expected": expected,
                        "actual": actual,
                    },
                })

    # ── Weekly teacher load check ────────────────────────────────────────────
    for teacher_id, count in teacher_weekly_load.items():
        if count > 28:
            teacher_name = teacher_lookup.get(teacher_id, {}).get("fullName", teacher_id)
            hard_errors.append({
                "type": "teacher_overload",
                "message": (
                    f"Teacher '{teacher_name}' is assigned {count} periods per week, "
                    "which exceeds the 28-period limit."
                ),
                "details": {
                    "teacherId": teacher_id,
                    "teacherName": teacher_name,
                    "scheduledPeriods": count,
                },
            })

    return {
        "is_valid": len(hard_errors) == 0,
        "errors": hard_errors + warnings,
        "hard_errors": hard_errors,
        "warnings": warnings,
    }
