import json
import logging
import random
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from app.config import GEMINI_API_KEY

try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency fallback
    genai = None


logger = logging.getLogger("uvicorn.error")

DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"

# ── Configurable constraints ─────────────────────────────────────────────────
PERIODS_PER_DAY = 8
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
# Total periods per week (8 periods/day * 5 days)
PERIODS_PER_WEEK = PERIODS_PER_DAY * len(DAYS)  # 40
MAX_TEACHER_WEEKLY_LOAD = 28
MAX_SOLVER_RESTARTS = 10
MAX_BACKTRACKS_PER_RESTART = 50_000

# Sentinel subject used to pad grades that have < 40 periods
_FREE_PERIOD_SUBJECT_ID = "__free_period__"
_FREE_PERIOD_TEACHER_ID = "__none__"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _normalize_id(value: Any) -> str:
    return str(value).strip()


def _normalize_subject_name(name: Any) -> str:
    return str(name).strip().lower()


def _build_teacher_lookup(teachers: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for teacher in teachers:
        teacher_id = _normalize_id(teacher.get("id", ""))
        if teacher_id:
            lookup[teacher_id] = teacher
    return lookup


def _build_qualification_map(teachers: List[Dict[str, Any]]) -> Dict[Tuple[str, int], List[str]]:
    qualification_map: Dict[Tuple[str, int], List[str]] = {}
    for teacher in teachers:
        teacher_id = _normalize_id(teacher.get("id", ""))
        if not teacher_id:
            continue

        for subject in teacher.get("subjects", []):
            subject_name = _normalize_subject_name(subject.get("name", ""))
            grades = subject.get("grades") or []
            for grade in grades:
                try:
                    grade_int = int(grade)
                except Exception:
                    continue
                qualification_map.setdefault((subject_name, grade_int), []).append(teacher_id)
    return qualification_map


def _allowed_teachers_for_subject(
    subject: Dict[str, Any],
    teacher_lookup: Dict[str, Dict[str, Any]],
    qualification_map: Dict[Tuple[str, int], List[str]],
) -> List[str]:
    """Returns list of teacher IDs qualified to teach the given subject at its grade."""
    assigned_teacher = _normalize_id(subject.get("assignedTeacher", ""))
    subject_name = _normalize_subject_name(subject.get("subjectName", ""))
    grade = subject.get("grade")
    allowed: List[str] = []

    if assigned_teacher and assigned_teacher in teacher_lookup:
        allowed.append(assigned_teacher)

    qualified = qualification_map.get((subject_name, int(grade)), []) if grade is not None else []
    for teacher_id in qualified:
        if teacher_id in teacher_lookup and teacher_id not in allowed:
            allowed.append(teacher_id)

    return allowed


# ── Pre-flight feasibility checks ───────────────────────────────────────────

def _preflight_check(
    grade_subjects: Dict[int, List[Dict[str, Any]]],
    teacher_lookup: Dict[str, Dict[str, Any]],
    qualification_map: Dict[Tuple[str, int], List[str]],
) -> List[str]:
    """
    Run sanity checks *before* entering the solver.
    Returns a list of fatal diagnostic error messages (empty = all OK).
    """
    diagnostics: List[str] = []

    for grade, subjects in sorted(grade_subjects.items()):
        grade_total = sum(int(s.get("periodsPerWeek", 0) or 0) for s in subjects)

        if grade_total > PERIODS_PER_WEEK:
            diagnostics.append(
                f"Grade {grade}: subjects require {grade_total} periods/week but only "
                f"{PERIODS_PER_WEEK} slots are available (overshoot by {grade_total - PERIODS_PER_WEEK}). "
                f"Reduce periodsPerWeek for some subjects."
            )

        teacher_demand: Dict[str, int] = defaultdict(int)
        for subj in subjects:
            teachers = _allowed_teachers_for_subject(subj, teacher_lookup, qualification_map)
            if not teachers:
                logger.warning(
                    "Grade %d, subject '%s' (id=%s): no qualified teacher found. "
                    "This subject will be left unassigned (blank periods).",
                    grade, subj.get('subjectName'), subj.get('id')
                )
                continue

            if len(teachers) == 1:
                teacher_demand[teachers[0]] += int(subj.get("periodsPerWeek", 0) or 0)

        for teacher_id, demand in sorted(teacher_demand.items(), key=lambda item: item[0]):
            if demand > MAX_TEACHER_WEEKLY_LOAD:
                teacher_name = teacher_lookup.get(teacher_id, {}).get("fullName", teacher_id)
                logger.warning(
                    "Teacher '%s' (id=%s) is the only teacher for subjects requiring %d periods/week, "
                    "which exceeds the %d limit. Excess periods will be left blank.",
                    teacher_name, teacher_id, demand, MAX_TEACHER_WEEKLY_LOAD
                )

    return diagnostics


# ── Deterministic solver with randomised restarts ────────────────────────────

def _build_deterministic_timetable(
    teachers: List[Dict[str, Any]],
    subjects: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Constraint-satisfaction solver that assigns subjects to (day, period) slots
    for each grade.  Uses backtracking with randomised candidate ordering and
    automatic restarts when the backtrack budget is exceeded.

    For each time slot, the solver simultaneously assigns one subject+teacher
    pair to every grade, ensuring no two grades share the same teacher in the
    same slot.
    """
    teacher_lookup = _build_teacher_lookup(teachers)
    qualification_map = _build_qualification_map(teachers)

    # ── Group subjects by grade ──────────────────────────────────────────────
    grade_subjects: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for subject in subjects:
        grade = subject.get("grade")
        if grade is None:
            continue
        try:
            grade_int = int(grade)
        except Exception:
            continue
        grade_subjects[grade_int].append(subject)

    if not grade_subjects:
        raise ValueError("No grade subjects available to generate a timetable.")

    # ── Pre-flight checks ────────────────────────────────────────────────────
    diagnostics = _preflight_check(grade_subjects, teacher_lookup, qualification_map)
    if diagnostics:
        raise ValueError(
            "Pre-flight constraint check failed:\n• " + "\n• ".join(diagnostics)
        )

    # ── Build per-grade subject info ─────────────────────────────────────────
    # For each grade, build a list of (subject_id, teacher_candidates, periods_remaining)
    # This allows the solver to CHOOSE which subject to place in each slot.

    grade_subject_info: Dict[int, List[Dict[str, Any]]] = {}
    for grade, slist in grade_subjects.items():
        info_list: List[Dict[str, Any]] = []
        total_periods = 0
        for subj in slist:
            subj_id = _normalize_id(subj.get("id", ""))
            ppw = int(subj.get("periodsPerWeek", 0) or 0)
            total_periods += ppw
            candidates = _allowed_teachers_for_subject(subj, teacher_lookup, qualification_map)
            info_list.append({
                "id": subj_id,
                "name": subj.get("subjectName", ""),
                "ppw": ppw,
                "candidates": candidates,
            })

        # Auto-pad with free periods if fewer than 40
        shortfall = PERIODS_PER_WEEK - total_periods
        if shortfall > 0:
            logger.info(
                "Grade %d has %d periods defined (need %d). Padding with %d free periods.",
                grade, total_periods, PERIODS_PER_WEEK, shortfall,
            )
            info_list.append({
                "id": _FREE_PERIOD_SUBJECT_ID,
                "name": "Free Period",
                "ppw": shortfall,
                "candidates": [_FREE_PERIOD_TEACHER_ID],
            })

        grade_subject_info[grade] = info_list

    # Diversify subject ordering per grade to reduce identical-looking timetables
    # across grades. Shuffle each grade's subject info so assignment order varies.
    for g in grade_subject_info:
        random.shuffle(grade_subject_info[g])

    grades = sorted(grade_subjects.keys())
    slots = [(day, period) for day in DAYS for period in range(1, PERIODS_PER_DAY + 1)]

    # ── Compute dynamic teacher weekly cap ───────────────────────────────────
    # Set the cap to the maximum any single teacher actually needs, so the
    # solver doesn't artificially reject feasible schedules.
    teacher_demand: Dict[str, int] = defaultdict(int)
    for grade, info_list in grade_subject_info.items():
        for info in info_list:
            if info["id"] == _FREE_PERIOD_SUBJECT_ID:
                continue
            for tid in info["candidates"]:
                # If there's only one candidate, this teacher MUST teach all periods
                if len(info["candidates"]) == 1:
                    teacher_demand[tid] += info["ppw"]
    # Teacher weekly load is a hard constraint. Allow only up to the configured
    # weekly maximum, even if a subject has multiple qualified teachers.
    max_teacher_cap = MAX_TEACHER_WEEKLY_LOAD
    logger.info("Teacher weekly cap set to %d", max_teacher_cap)

    # ── Solver with restarts ─────────────────────────────────────────────────
    last_failure_info: Optional[str] = None

    for restart in range(1, MAX_SOLVER_RESTARTS + 1):
        logger.info("Solver restart %d / %d", restart, MAX_SOLVER_RESTARTS)

        # Deep copy remaining counts per grade per subject
        remaining: Dict[int, Dict[str, int]] = {
            grade: {info["id"]: info["ppw"] for info in info_list}
            for grade, info_list in grade_subject_info.items()
        }

        # Subject candidate lookup (grade -> subject_id -> teacher_candidates)
        candidates_lookup: Dict[int, Dict[str, List[str]]] = {
            grade: {info["id"]: list(info["candidates"]) for info in info_list}
            for grade, info_list in grade_subject_info.items()
        }

        # Shuffle candidate lists per subject to add randomness and rotate
        # preferences so similar grade inputs don't produce identical outputs.
        for g, submap in candidates_lookup.items():
            for sid, clist in submap.items():
                random.shuffle(clist)

        # Tracking structures
        timetable: Dict[str, Any] = {
            f"{grade}A": {day: [] for day in DAYS} for grade in grades
        }
        teacher_schedule: Dict[str, Dict[int, set]] = {
            day: {period: set() for period in range(1, PERIODS_PER_DAY + 1)} for day in DAYS
        }
        teacher_weekly_load: Dict[str, int] = {tid: 0 for tid in teacher_lookup}
        teacher_weekly_load[_FREE_PERIOD_TEACHER_ID] = 0

        backtrack_count = 0
        budget_exceeded = False

        def _try_slot(slot_idx: int) -> bool:
            nonlocal backtrack_count, budget_exceeded, last_failure_info

            if budget_exceeded:
                return False

            if slot_idx >= len(slots):
                return True

            day, period = slots[slot_idx]
                # For this slot, assign one subject+teacher per grade.
                # Process grades in a random order for diversity.
            grade_order = list(grades)
            random.shuffle(grade_order)

            def _assign_grade(gidx: int) -> bool:
                nonlocal backtrack_count, budget_exceeded, last_failure_info

                if budget_exceeded:
                    return False

                if gidx >= len(grade_order):
                    return _try_slot(slot_idx + 1)

                grade = grade_order[gidx]

                # Collect all subjects with remaining periods for this grade
                choosable: List[Tuple[str, List[str]]] = []
                for sid, rem in remaining[grade].items():
                    if rem > 0:
                        choosable.append((sid, candidates_lookup[grade][sid]))

                if not choosable:
                    # All subjects for this grade are fully scheduled — skip
                    return _assign_grade(gidx + 1)

                # Collect real subject options that have available teachers in this slot
                valid_options = []
                for sid, cands in choosable:
                    if sid == _FREE_PERIOD_SUBJECT_ID:
                        continue
                    avail = [
                        tid for tid in cands
                        if tid not in teacher_schedule[day][period]
                        and teacher_weekly_load.get(tid, 0) < max_teacher_cap
                    ]
                    if avail:
                        valid_options.append((sid, avail))

                if valid_options:
                    # Randomize order slightly to avoid deterministic tie patterns,
                    # then sort by fewest available teachers and most remaining periods.
                    random.shuffle(valid_options)
                    valid_options.sort(key=lambda item: (len(item[1]), -remaining[grade][item[0]]))

                    for sid, avail_teachers in valid_options:
                        # rotate available teachers list by grade index to bias different
                        # grades toward different teacher choices when multiple options exist
                        random.shuffle(avail_teachers)
                        try:
                            shift = grade % max(1, len(avail_teachers))
                        except Exception:
                            shift = 0
                        if shift and len(avail_teachers) > 1:
                            avail_teachers = avail_teachers[shift:] + avail_teachers[:shift]
                        avail_teachers.sort(key=lambda tid: teacher_weekly_load.get(tid, 0))

                        for tid in avail_teachers:
                            timetable[f"{grade}A"][day].append({
                                "period": period,
                                "subjectId": sid,
                                "teacherId": tid,
                            })
                            teacher_schedule[day][period].add(tid)
                            teacher_weekly_load[tid] += 1
                            remaining[grade][sid] -= 1

                            if _assign_grade(gidx + 1):
                                return True

                            remaining[grade][sid] += 1
                            teacher_weekly_load[tid] -= 1
                            teacher_schedule[day][period].discard(tid)
                            timetable[f"{grade}A"][day].pop()

                            backtrack_count += 1
                            if backtrack_count >= MAX_BACKTRACKS_PER_RESTART:
                                budget_exceeded = True
                                return False

                # Free period option (either explicitly defined shortfall, or as a blank fallback if no real subject could be assigned)
                has_free_period_rem = remaining[grade].get(_FREE_PERIOD_SUBJECT_ID, 0) > 0

                if has_free_period_rem or not valid_options:
                    timetable[f"{grade}A"][day].append({
                        "period": period,
                        "subjectId": _FREE_PERIOD_SUBJECT_ID,
                        "teacherId": _FREE_PERIOD_TEACHER_ID,
                    })
                    if has_free_period_rem:
                        remaining[grade][_FREE_PERIOD_SUBJECT_ID] -= 1

                    if _assign_grade(gidx + 1):
                        return True

                    if has_free_period_rem:
                        remaining[grade][_FREE_PERIOD_SUBJECT_ID] += 1
                    timetable[f"{grade}A"][day].pop()

                    backtrack_count += 1
                    if backtrack_count >= MAX_BACKTRACKS_PER_RESTART:
                        budget_exceeded = True
                        return False

                last_failure_info = (
                    f"Grade {grade}, {day} P{period}: could not assign any subject. "
                    f"Remaining subjects: {[(sid, remaining[grade][sid]) for sid, _ in choosable if remaining[grade][sid] > 0]}"
                )
                return False

            return _assign_grade(0)

        if _try_slot(0):
            logger.info("Solver succeeded on restart %d (backtracks: %d)", restart, backtrack_count)

            # Strip free-period sentinels from the output
            for class_key in timetable:
                for day in DAYS:
                    timetable[class_key][day] = [
                        entry for entry in timetable[class_key][day]
                        if entry["subjectId"] != _FREE_PERIOD_SUBJECT_ID
                    ]

            return timetable

        logger.warning(
            "Solver restart %d exhausted backtrack budget (%d). %s",
            restart, backtrack_count,
            last_failure_info or "No specific failure info.",
        )

    # All restarts exhausted
    detail = (
        f"Unable to build a valid timetable after {MAX_SOLVER_RESTARTS} solver restarts "
        f"(each with {MAX_BACKTRACKS_PER_RESTART:,} backtrack budget)."
    )
    if last_failure_info:
        detail += f"\nLast failure: {last_failure_info}"

    raise ValueError(detail)


# ── Gemini AI fallback ───────────────────────────────────────────────────────

async def _generate_via_gemini(
    teachers: List[Dict[str, Any]],
    subjects: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Attempt to generate a timetable using Gemini AI.
    Returns the parsed JSON dict on success, or None on failure.
    """
    if not GEMINI_API_KEY or genai is None:
        return None

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
You are an expert school timetable generator.

Generate a weekly timetable for each class separately.

Rules

1. Monday-Friday only.
2. 8 periods per day.
3. Each grade must contain exactly required weekly periods.
4. A teacher MUST never teach two grades in the same period.
5. Do NOT create teacher clashes.
6. Respect assignedTeacher for each subject when possible.
7. If more than one teacher can teach the same subject, distribute workload evenly.
8. Return ONLY valid JSON.

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
    except Exception as exc:
        logger.warning("Gemini API call failed: %s", exc)
        return None

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        logger.warning("Gemini returned invalid JSON: %s", exc)
        return None


async def generate_timetable(
    teachers: List[Dict[str, Any]],
    subjects: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Primary entry point.  Tries the deterministic solver first, then falls back
    to Gemini AI if the solver raises ValueError.
    """
    try:
        return _build_deterministic_timetable(teachers, subjects)
    except ValueError as solver_error:
        logger.warning("Deterministic solver failed: %s — trying Gemini AI fallback.", solver_error)

        gemini_result = await _generate_via_gemini(teachers, subjects)
        if gemini_result is not None:
            logger.info("Gemini AI produced a timetable; returning it for validation.")
            return gemini_result

        # Neither solver nor Gemini succeeded — re-raise the original solver error
        # with full diagnostic context so the caller can surface it.
        raise


async def generate_timetable_from_ai(
    teachers: List[Dict[str, Any]] | None = None,
    subjects: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    return await generate_timetable(teachers or [], subjects or [])
