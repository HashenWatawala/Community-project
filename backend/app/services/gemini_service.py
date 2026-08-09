import json
from typing import Any, Dict, List

from app.config import GEMINI_API_KEY

try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency fallback
    genai = None


DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


def _build_fallback_timetable(teachers: List[Dict[str, Any]], subjects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a deterministic timetable payload that satisfies the app's expected shape."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    timetable: Dict[str, Any] = {}
    teacher_ids = [str(t.get("id", "")).strip() for t in teachers if str(t.get("id", "")).strip()]
    if not teacher_ids:
        teacher_ids = [f"teacher-{index}" for index in range(1, 7)]

    for grade in range(6, 12):
        class_name = f"{grade}A"
        grade_subjects = [s for s in subjects if s.get("grade") == grade]
        if not grade_subjects:
            continue

        remaining_counts: Dict[str, int] = {}
        for subject in grade_subjects:
            subject_id = str(subject.get("id", ""))
            count = int(subject.get("periodsPerWeek", 0) or 0)
            if count <= 0:
                count = 8
            remaining_counts[subject_id] = count

        class_schedule: Dict[str, List[Dict[str, Any]]] = {day: [] for day in days}
        for day in days:
            for period in range(1, 9):
                selected_subject = None
                selected_teacher = ""
                for subject in grade_subjects:
                    subject_id = str(subject.get("id", ""))
                    if remaining_counts[subject_id] <= 0:
                        continue
                    teacher_id = str(subject.get("assignedTeacher", "")).strip()
                    if not teacher_id:
                        teacher_id = teacher_ids[0]
                    if teacher_id in {(entry.get("teacherId", "") for entry in class_schedule[day])}:
                        continue
                    selected_subject = subject
                    selected_teacher = teacher_id
                    break

                if selected_subject is None:
                    continue

                subject_id = str(selected_subject.get("id", ""))
                remaining_counts[subject_id] -= 1
                class_schedule[day].append(
                    {
                        "period": period,
                        "subjectId": subject_id,
                        "teacherId": selected_teacher,
                    }
                )

        timetable[class_name] = class_schedule

    return timetable


async def generate_timetable(teachers: List[Dict[str, Any]], subjects: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not GEMINI_API_KEY or genai is None:
        return _build_fallback_timetable(teachers, subjects)

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
You are an expert school timetable generator.

Generate a weekly timetable.

Rules

1. Monday-Friday only.

2. 8 periods per day.

3. Each grade must contain exactly required weekly periods.

4. A teacher CANNOT teach two grades in the same period.

5. Do NOT create teacher clashes.

6. Use assignedTeacher from subjects.

7. Return ONLY valid JSON.

Teachers

{json.dumps(teachers, indent=2)}

Subjects

{json.dumps(subjects, indent=2)}

Output format

{{
    "6A": {{"Monday": []}},
    "7A": {{"Monday": []}},
    "8A": {{"Monday": []}},
    "9A": {{"Monday": []}},
    "10A": {{"Monday": []}},
    "11A": {{"Monday": []}}
}}

Return JSON only.
"""

    try:
        response = client.models.generate_content(model=DEFAULT_GEMINI_MODEL, contents=prompt)
        text = response.text.strip()
    except Exception:
        return _build_fallback_timetable(teachers, subjects)

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _build_fallback_timetable(teachers, subjects)


async def generate_timetable_from_ai(teachers: List[Dict[str, Any]] | None = None, subjects: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    return await generate_timetable(teachers or [], subjects or [])
