from __future__ import annotations

from typing import Any, Dict, List


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
    4. Teacher Assignment — only the assigned teacher may teach a subject.
    5. Missing Periods  — each class must have all 8 periods on every weekday.
    6. Grade Subject Match — a class may only use subjects belonging to its grade.

    Returns:
        {"is_valid": bool, "errors": List[Dict[str, Any]]}
    """
    errors: List[Dict[str, Any]] = []

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

    # ── Check that all expected classes are present ───────────────────────────
    for cls in expected_classes:
        if cls not in timetable_data:
            errors.append({
                "type": "missing_class",
                "message": f"Class {cls} is missing from the generated timetable.",
                "details": {"class": cls},
            })

    active_classes = [c for c in expected_classes if c in timetable_data]

    # ── Per-day teacher occupancy: day → period → teacher_id → [classes] ──────
    teacher_schedule: Dict[str, Dict[int, Dict[str, List[str]]]] = {
        day: {p: {} for p in range(1, 9)} for day in days_of_week
    }

    # ── Per-class subject counters: class → subject_id → count ───────────────
    subject_counts: Dict[str, Dict[str, int]] = {cls: {} for cls in active_classes}

    for class_name in active_classes:
        # Extract numeric grade from class name (e.g. "6A" → 6, "10A" → 10)
        try:
            class_grade = int(class_name[:-1])
        except ValueError:
            errors.append({
                "type": "invalid_class_name",
                "message": f"Cannot parse grade from class name: {class_name}",
                "details": {"class": class_name},
            })
            continue

        class_schedule = timetable_data[class_name]

        for day in days_of_week:
            # ── Day presence ──────────────────────────────────────────────────
            if day not in class_schedule:
                errors.append({
                    "type": "missing_day",
                    "message": f"Day '{day}' missing in schedule for class {class_name}.",
                    "details": {"class": class_name, "day": day},
                })
                continue

            periods_list = class_schedule[day]
            if not isinstance(periods_list, list):
                errors.append({
                    "type": "invalid_day_format",
                    "message": f"Schedule for {class_name}/{day} must be a list.",
                    "details": {"class": class_name, "day": day},
                })
                continue

            seen_periods: set = set()

            for entry in periods_list:
                if not isinstance(entry, dict):
                    errors.append({
                        "type": "invalid_period_format",
                        "message": f"Period entry in {class_name}/{day} must be an object.",
                        "details": {"class": class_name, "day": day},
                    })
                    continue

                p_num = entry.get("period")
                raw_sub_id = entry.get("subjectId", "")
                raw_teach_id = entry.get("teacherId", "")

                # Normalise IDs
                sub_id = str(raw_sub_id).strip()
                teach_id = str(raw_teach_id).strip()

                # ── Required fields ────────────────────────────────────────────
                if p_num is None or not sub_id or not teach_id:
                    errors.append({
                        "type": "incomplete_period_entry",
                        "message": (
                            f"Incomplete period entry in {class_name}/{day}. "
                            "Must contain period, subjectId, and teacherId."
                        ),
                        "details": {"class": class_name, "day": day, "entry": entry},
                    })
                    continue

                # ── Period range ────────────────────────────────────────────────
                if not isinstance(p_num, int) or p_num < 1 or p_num > 8:
                    errors.append({
                        "type": "invalid_period_number",
                        "message": f"Period {p_num} in {class_name}/{day} is out of range (1–8).",
                        "details": {"class": class_name, "day": day, "period": p_num},
                    })
                    continue

                # ── Duplicate period (period clash within class) ────────────────
                if p_num in seen_periods:
                    errors.append({
                        "type": "period_clash",
                        "message": f"Period {p_num} appears more than once for {class_name}/{day}.",
                        "details": {"class": class_name, "day": day, "period": p_num},
                    })
                seen_periods.add(p_num)

                # ── Subject exists in DB ────────────────────────────────────────
                subject = subject_lookup.get(sub_id)
                if not subject:
                    errors.append({
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
                    errors.append({
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

                # ── Teacher assignment ──────────────────────────────────────────
                # Normalise both sides to stripped strings for comparison
                expected_teach_id = str(subject.get("assignedTeacher", "")).strip()
                if expected_teach_id and expected_teach_id != teach_id:
                    expected_t = teacher_lookup.get(expected_teach_id)
                    actual_t = teacher_lookup.get(teach_id)
                    expected_name = expected_t["fullName"] if expected_t else expected_teach_id
                    actual_name = actual_t["fullName"] if actual_t else teach_id
                    errors.append({
                        "type": "invalid_teacher_assignment",
                        "message": (
                            f"Wrong teacher for '{subject['subjectName']}' in {class_name}/{day} P{p_num}. "
                            f"Expected '{expected_name}' but got '{actual_name}'."
                        ),
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

            # ── Missing periods for this class/day ─────────────────────────────
            missing = [p for p in range(1, 9) if p not in seen_periods]
            if missing:
                errors.append({
                    "type": "missing_periods",
                    "message": f"{class_name}/{day} is missing periods: {missing}.",
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
                    errors.append({
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

    # ── Weekly subject count check ────────────────────────────────────────────
    for class_name in active_classes:
        class_grade = int(class_name[:-1])
        grade_subjects = [s for s in subjects if s["grade"] == class_grade]

        for subject in grade_subjects:
            sub_id = str(subject["id"]).strip()
            expected = subject["periodsPerWeek"]
            actual = subject_counts[class_name].get(sub_id, 0)

            if actual != expected:
                errors.append({
                    "type": "subject_count_mismatch",
                    "message": (
                        f"'{subject['subjectName']}' in {class_name}: "
                        f"scheduled {actual} times but requires {expected} periods/week."
                    ),
                    "details": {
                        "class": class_name,
                        "subjectId": sub_id,
                        "subjectName": subject["subjectName"],
                        "expected": expected,
                        "actual": actual,
                    },
                })

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }
