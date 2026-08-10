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

    timetable = _build_deterministic_timetable(teachers, subjects)

    assert "6A" in timetable
    assert "7A" in timetable
    assert "8A" in timetable
    assert "9A" in timetable
    assert "10A" in timetable
    assert "11A" in timetable

    val_res = validate_timetable(timetable, subjects, teachers)
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

    timetable = _build_deterministic_timetable(teachers, subjects)

    assert "6A" in timetable
    assert "7A" in timetable
    
    # Grade 6 Math entries should be present
    math_entries = [
        entry for day_entries in timetable["6A"].values() for entry in day_entries if entry["subjectId"] == "sub_1"
    ]
    assert len(math_entries) == 10

    # Validator checks: should pass without hard errors, producing blank periods for Grade 6
    val_res = validate_timetable(timetable, subjects, teachers)
    assert val_res["is_valid"] is True
    assert len(val_res["hard_errors"]) == 0
    assert any(w["type"] == "missing_periods" for w in val_res["warnings"])
