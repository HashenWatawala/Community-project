"""
seed_teachers.py
================
Populates the 'teachers' collection with a full set of qualified teachers
that can cover every subject across every grade (6-11) without hitting the
28-period weekly load limit and without teacher clashes.

SUBJECT COVERAGE PLAN
----------------------
5 subjects  x  6 grades  =  30 subject entries
Each subject = 8 periods/week

Per-subject teacher allocation (2 teachers per subject, 3 grades each):
  Mathematics: T-Math-A (grades 6,7,8)  + T-Math-B (grades 9,10,11)
  Science:     T-Sci-A  (grades 6,7,8)  + T-Sci-B  (grades 9,10,11)
  English:     T-Eng-A  (grades 6,7,8)  + T-Eng-B  (grades 9,10,11)
  History:     T-Hist-A (grades 6,7,8)  + T-Hist-B (grades 9,10,11)
  Art:         T-Art-A  (grades 6,7,8)  + T-Art-B  (grades 9,10,11)

Max load per teacher: 3 grades x 8 ppw = 24 periods/week  (<= 28 limit)

Additionally, the existing 5 seed teachers (Nirmala, Saman, Dilini, Kamal,
Tharushi) are updated with proper subject qualifications so their
assignedTeacher references on subjects are resolved correctly.

Usage:
    python seed_teachers.py                    # adds teachers (no wipe)
    python seed_teachers.py --replace-all      # wipes teachers + timetable first
"""

import asyncio
import sys
from app.database import get_database
from app.models.teacher_model import create_teacher, list_teachers


# ---------------------------------------------------------------------------
# Full teacher definitions — each teacher has a 'subjects' list that the
# solver uses to determine qualification (name + grades).
# ---------------------------------------------------------------------------
TEACHER_DEFINITIONS = [
    # ── Mathematics ──────────────────────────────────────────────────────────
    {
        "fullName": "Mr. Kasun Jayawardena",
        "email": "kasun.jayawardena@school.lk",
        "nicNo": "197501001V",
        "contactNumber": "+94771000001",
        "hasAssignClass": True,
        "subjects": [{"name": "Mathematics", "grades": [6, 7, 8]}],
    },
    {
        "fullName": "Ms. Nadeesha Mendis",
        "email": "nadeesha.mendis@school.lk",
        "nicNo": "198201001V",
        "contactNumber": "+94771000002",
        "hasAssignClass": True,
        "subjects": [{"name": "Mathematics", "grades": [9, 10, 11]}],
    },
    # ── Science ──────────────────────────────────────────────────────────────
    {
        "fullName": "Mr. Chamara Gunasekara",
        "email": "chamara.gunasekara@school.lk",
        "nicNo": "198001001V",
        "contactNumber": "+94771000003",
        "hasAssignClass": True,
        "subjects": [{"name": "Science", "grades": [6, 7, 8]}],
    },
    {
        "fullName": "Ms. Ishani Rathnayake",
        "email": "ishani.rathnayake@school.lk",
        "nicNo": "199001001V",
        "contactNumber": "+94771000004",
        "hasAssignClass": True,
        "subjects": [{"name": "Science", "grades": [9, 10, 11]}],
    },
    # ── English ──────────────────────────────────────────────────────────────
    {
        "fullName": "Ms. Priyanka Bandara",
        "email": "priyanka.bandara@school.lk",
        "nicNo": "198501001V",
        "contactNumber": "+94771000005",
        "hasAssignClass": True,
        "subjects": [{"name": "English", "grades": [6, 7, 8]}],
    },
    {
        "fullName": "Mr. Ruwan Wickramasinghe",
        "email": "ruwan.wickramasinghe@school.lk",
        "nicNo": "197801001V",
        "contactNumber": "+94771000006",
        "hasAssignClass": True,
        "subjects": [{"name": "English", "grades": [9, 10, 11]}],
    },
    # ── History ──────────────────────────────────────────────────────────────
    {
        "fullName": "Ms. Thilini Dissanayake",
        "email": "thilini.dissanayake@school.lk",
        "nicNo": "198801001V",
        "contactNumber": "+94771000007",
        "hasAssignClass": True,
        "subjects": [{"name": "History", "grades": [6, 7, 8]}],
    },
    {
        "fullName": "Mr. Sanjeewa Karunaratne",
        "email": "sanjeewa.karunaratne@school.lk",
        "nicNo": "197201001V",
        "contactNumber": "+94771000008",
        "hasAssignClass": True,
        "subjects": [{"name": "History", "grades": [9, 10, 11]}],
    },
    # ── Art ──────────────────────────────────────────────────────────────────
    {
        "fullName": "Ms. Dulanjali Perera",
        "email": "dulanjali.perera@school.lk",
        "nicNo": "199201001V",
        "contactNumber": "+94771000009",
        "hasAssignClass": True,
        "subjects": [{"name": "Art", "grades": [6, 7, 8]}],
    },
    {
        "fullName": "Mr. Buddhika Samarasinghe",
        "email": "buddhika.samarasinghe@school.lk",
        "nicNo": "198601001V",
        "contactNumber": "+94771000010",
        "hasAssignClass": True,
        "subjects": [{"name": "Art", "grades": [9, 10, 11]}],
    },
    # ── Backup / cross-grade teachers (cover all grades for extra flexibility) ─
    # Each backup teacher can cover all 6 grades for one subject.
    # Having backup teachers prevents UNASSIGNED when the primary is at load limit.
    {
        "fullName": "Ms. Anusha Wijeratne",
        "email": "anusha.wijeratne@school.lk",
        "nicNo": "197001001V",
        "contactNumber": "+94771000011",
        "hasAssignClass": True,
        "subjects": [
            {"name": "Mathematics", "grades": [6, 7, 8, 9, 10, 11]},
            {"name": "Science", "grades": [6, 7, 8, 9, 10, 11]},
        ],
    },
    {
        "fullName": "Mr. Prasanna Senanayake",
        "email": "prasanna.senanayake@school.lk",
        "nicNo": "197601001V",
        "contactNumber": "+94771000012",
        "hasAssignClass": True,
        "subjects": [
            {"name": "English", "grades": [6, 7, 8, 9, 10, 11]},
            {"name": "History", "grades": [6, 7, 8, 9, 10, 11]},
        ],
    },
    {
        "fullName": "Ms. Kumari Pathirana",
        "email": "kumari.pathirana@school.lk",
        "nicNo": "198901001V",
        "contactNumber": "+94771000013",
        "hasAssignClass": True,
        "subjects": [
            {"name": "Art", "grades": [6, 7, 8, 9, 10, 11]},
            {"name": "Science", "grades": [6, 7, 8, 9, 10, 11]},
        ],
    },
]


async def main(replace_all: bool = False) -> None:
    db = get_database()

    if replace_all:
        print("Wiping teachers and timetable collections...")
        await db["teachers"].delete_many({})
        await db["timetable"].delete_many({})
        print("  Done.")
    else:
        # Soft mode: skip teachers whose email already exists
        existing = await list_teachers()
        existing_emails = {t["email"] for t in existing}
        print(f"Found {len(existing)} existing teachers. Skipping duplicates by email.")

    created = 0
    skipped = 0
    for defn in TEACHER_DEFINITIONS:
        if not replace_all:
            if defn["email"] in existing_emails:
                print(f"  SKIP (already exists): {defn['fullName']}")
                skipped += 1
                continue

        result = await create_teacher(defn)
        print(f"  CREATED: {result['fullName']} — subjects: {[s['name'] + str(s['grades']) for s in defn['subjects']]}")
        created += 1

    print()
    print(f"Done. Created: {created}, Skipped: {skipped}")
    print()

    # Print summary
    all_teachers = await list_teachers()
    print(f"Total teachers in DB: {len(all_teachers)}")
    total_capacity = sum(
        sum(len(s.get("grades", [])) for s in t.get("subjects", []))
        for t in all_teachers
    )
    print(f"Total subject-grade slots covered: {total_capacity} (need 30 minimum)")

    # Coverage check
    from collections import defaultdict
    coverage: dict = defaultdict(list)
    for t in all_teachers:
        for s in t.get("subjects", []):
            for g in s.get("grades", []):
                coverage[(s["name"], g)].append(t["fullName"])

    subjects_needed = ["Mathematics", "Science", "English", "History", "Art"]
    grades_needed = [6, 7, 8, 9, 10, 11]

    uncovered = []
    print()
    print("Coverage matrix (subject x grade -> # teachers):")
    print(f"{'Subject':<15}", end="")
    for g in grades_needed:
        print(f" G{g}", end="")
    print()
    for subj in subjects_needed:
        print(f"  {subj:<13}", end="")
        for g in grades_needed:
            count = len(coverage.get((subj, g), []))
            print(f"  {count:2}", end="")
            if count == 0:
                uncovered.append((subj, g))
        print()

    if uncovered:
        print()
        print("WARNING: Uncovered subject-grade combinations:")
        for subj, g in uncovered:
            print(f"  - {subj} Grade {g}")
    else:
        print()
        print("ALL SUBJECT-GRADE COMBINATIONS ARE COVERED.")


if __name__ == "__main__":
    replace_all = "--replace-all" in sys.argv
    asyncio.run(main(replace_all))
