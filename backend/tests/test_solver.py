import pytest
from app.services.gemini_service import _build_deterministic_timetable
from app.services.timetable_validator import validate_timetable


def test_solver_with_varying_periods_and_shared_teachers():
    # 6 grades (6..11) with non-uniform periodsPerWeek totalling 40 periods per grade
    periods_dist = [6, 6, 5, 5, 5, 4, 4, 3, 2]  # sum = 40
    teacher_ids_678 = [f"t_678_{i}" for i in range(8)]
    teacher_ids_91011 = [f"t_91011_{i}" for i in range(8)]

    teachers = []
    for tid in teacher_ids_678 + teacher_ids_91011:
        teachers.append({"id": tid, "fullName": f"Teacher {tid}", "subjects": []})

    subjects = []
    sub_id = 1

    for g in range(6, 9):
        for idx, ppw in enumerate(periods_dist):
            tid = teacher_ids_678[idx % len(teacher_ids_678)]
            subjects.append({
                "id": f"sub_{sub_id}",
                "grade": g,
                "subjectName": f"Subject_{idx}",
                "periodsPerWeek": ppw,
                "assignedTeacher": tid,
            })
            sub_id += 1

    for g in range(9, 12):
        for idx, ppw in enumerate(periods_dist):
            tid = teacher_ids_91011[idx % len(teacher_ids_91011)]
            subjects.append({
                "id": f"sub_{sub_id}",
                "grade": g,
                "subjectName": f"Subject_{idx}",
                "periodsPerWeek": ppw,
                "assignedTeacher": tid,
            })
            sub_id += 1

    result = _build_deterministic_timetable(teachers, subjects)
    timetable = result["timetable"]

    assert "6A" in timetable
    assert "7A" in timetable
    assert "8A" in timetable
    assert "9A" in timetable
    assert "10A" in timetable
    assert "11A" in timetable

    val_res = validate_timetable(result, subjects, teachers)
    assert val_res["is_valid"] is True
    assert len(val_res["hard_errors"]) == 0


def test_solver_leaves_blank_periods_when_teachers_missing():
    # Grades 6..11 provided, but Grade 6 has Science/English with NO teachers assigned
    teachers = [{"id": f"t_{g}", "fullName": f"Teacher {g}", "subjects": []} for g in range(6, 12)]
    subjects = []
    sub_id = 1
    
    # Grade 6 has Math (assigned to t_6) and Science/English (unassigned)
    subjects.append({"id": f"sub_{sub_id}", "grade": 6, "subjectName": "Math", "periodsPerWeek": 10, "assignedTeacher": "t_6"})
    sub_id += 1
    subjects.append({"id": f"sub_{sub_id}", "grade": 6, "subjectName": "Science", "periodsPerWeek": 10, "assignedTeacher": ""})
    sub_id += 1
    subjects.append({"id": f"sub_{sub_id}", "grade": 6, "subjectName": "English", "periodsPerWeek": 10, "assignedTeacher": ""})
    sub_id += 1

    # Grades 7..11 have valid assigned teachers
    for g in range(7, 12):
        subjects.append({"id": f"sub_{sub_id}", "grade": g, "subjectName": "Math", "periodsPerWeek": 40, "assignedTeacher": f"t_{g}"})
        sub_id += 1

    result = _build_deterministic_timetable(teachers, subjects)
    timetable = result["timetable"]

    assert "6A" in timetable
    assert "7A" in timetable
    
    # Grade 6 Math entries should be present
    math_entries = [
        entry for day_entries in timetable["6A"].values() for entry in day_entries if entry["subjectId"] == "sub_1"
    ]
    assert len(math_entries) == 10

    # Validator checks: should pass without hard errors, producing unassigned warnings for Grade 6
    val_res = validate_timetable(result, subjects, teachers)
    assert val_res["is_valid"] is True
    assert len(val_res["hard_errors"]) == 0
    assert any(w["type"] == "unassigned_teacher" for w in val_res["warnings"])


def test_solver_consistent_teacher_per_grade_subject():
    """
    When multiple teachers are qualified for the same subject in a grade,
    the solver must pick exactly ONE teacher and use that teacher for all
    periods of that (grade, subject) pair throughout the week.
    """
    # Create 3 teachers, each qualified to teach Math AND Science for grades 6-11
    teachers = []
    for i in range(1, 4):
        teachers.append({
            "id": f"t_{i}",
            "fullName": f"Teacher {i}",
            "subjects": [
                {"name": "Math", "grades": [6, 7, 8, 9, 10, 11]},
                {"name": "Science", "grades": [6, 7, 8, 9, 10, 11]},
            ],
        })

    # Each grade has Math (20 ppw) and Science (20 ppw) = 40 total
    subjects = []
    sub_id = 1
    for g in range(6, 12):
        subjects.append({
            "id": f"sub_{sub_id}",
            "grade": g,
            "subjectName": "Math",
            "periodsPerWeek": 20,
            "assignedTeacher": "t_1",  # preferred, but t_2 and t_3 also qualify
        })
        sub_id += 1
        subjects.append({
            "id": f"sub_{sub_id}",
            "grade": g,
            "subjectName": "Science",
            "periodsPerWeek": 20,
            "assignedTeacher": "t_2",  # preferred, but t_1 and t_3 also qualify
        })
        sub_id += 1

    result = _build_deterministic_timetable(teachers, subjects)
    timetable = result["timetable"]

    # For every class, every subject should map to exactly one teacher
    for class_key, days_schedule in timetable.items():
        subject_teacher_map = {}
        for day, entries in days_schedule.items():
            for entry in entries:
                sid = entry["subjectId"]
                tid = entry.get("teacherId")
                status = entry.get("teacherAssignmentStatus", "")
                if status == "UNASSIGNED" or tid is None:
                    continue
                if sid not in subject_teacher_map:
                    subject_teacher_map[sid] = tid
                else:
                    assert subject_teacher_map[sid] == tid, (
                        f"{class_key}: subject {sid} has inconsistent teachers: "
                        f"{subject_teacher_map[sid]} vs {tid}"
                    )

    # Validator should also pass with no hard errors
    val_res = validate_timetable(result, subjects, teachers)
    assert val_res["is_valid"] is True, (
        f"Validation failed with hard errors: {val_res['hard_errors']}"
    )
    assert len(val_res["hard_errors"]) == 0
    # Specifically, no inconsistent_teacher errors
    assert not any(e["type"] == "inconsistent_teacher" for e in val_res["hard_errors"])

