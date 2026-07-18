import asyncio

from app.database import get_database
from app.models.subject_model import create_subject
from app.models.teacher_model import create_teacher


async def seed_sample_data() -> None:
    db = get_database()
    await db["teachers"].delete_many({})
    await db["subjects"].delete_many({})
    await db["timetable"].delete_many({})

    teacher_payloads = [
        {
            "fullName": "Ms. Nirmala Silva",
            "email": "nirmala@example.com",
            "nicNo": "199001001V",
            "contactNumber": "+94770000001",
            "hasAssignClass": True,
            "subjects": [],
        },
        {
            "fullName": "Mr. Saman Perera",
            "email": "saman@example.com",
            "nicNo": "198801001V",
            "contactNumber": "+94770000002",
            "hasAssignClass": True,
            "subjects": [],
        },
        {
            "fullName": "Ms. Dilini Fernando",
            "email": "dilini@example.com",
            "nicNo": "199201001V",
            "contactNumber": "+94770000003",
            "hasAssignClass": True,
            "subjects": [],
        },
        {
            "fullName": "Mr. Kamal Jayasekara",
            "email": "kamal@example.com",
            "nicNo": "198701001V",
            "contactNumber": "+94770000004",
            "hasAssignClass": True,
            "subjects": [],
        },
        {
            "fullName": "Ms. Tharushi Ranasinghe",
            "email": "tharushi@example.com",
            "nicNo": "199501001V",
            "contactNumber": "+94770000005",
            "hasAssignClass": True,
            "subjects": [],
        },
        {
            "fullName": "Mr. Dilan Wijesinghe",
            "email": "dilan@example.com",
            "nicNo": "199101001V",
            "contactNumber": "+94770000006",
            "hasAssignClass": True,
            "subjects": [],
        },
    ]

    created_teachers = []
    for payload in teacher_payloads:
        created_teachers.append(await create_teacher(payload))

    teacher_ids = [teacher["id"] for teacher in created_teachers]
    grade_teacher_map = {
        6: [teacher_ids[0], teacher_ids[1], teacher_ids[2], teacher_ids[3], teacher_ids[4]],
        7: [teacher_ids[1], teacher_ids[2], teacher_ids[3], teacher_ids[4], teacher_ids[5]],
        8: [teacher_ids[2], teacher_ids[3], teacher_ids[4], teacher_ids[5], teacher_ids[0]],
        9: [teacher_ids[3], teacher_ids[4], teacher_ids[5], teacher_ids[0], teacher_ids[1]],
        10: [teacher_ids[4], teacher_ids[5], teacher_ids[0], teacher_ids[1], teacher_ids[2]],
        11: [teacher_ids[5], teacher_ids[0], teacher_ids[1], teacher_ids[2], teacher_ids[3]],
    }

    subjects = []
    for grade in range(6, 12):
        teacher_list = grade_teacher_map[grade]
        subject_names = ["Mathematics", "Science", "English", "History", "Art"]
        for name, teacher_id in zip(subject_names, teacher_list):
            subjects.append(
                {
                    "grade": grade,
                    "subjectName": name,
                    "periodsPerWeek": 8,
                    "assignedTeacher": teacher_id,
                }
            )

    for payload in subjects:
        await create_subject(payload)

    print("Seeded teachers and subjects successfully.")


if __name__ == "__main__":
    asyncio.run(seed_sample_data())
