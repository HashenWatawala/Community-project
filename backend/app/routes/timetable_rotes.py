from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from app.database import get_database


router = APIRouter(
    prefix="/api/timetable",
    tags=["timetable"]
)


@router.get("")
async def get_timetable(grade: str = Query(...)):

    db = get_database()

    timetable_doc = await db["timetable"].find_one(
        {"generated": True},
        sort=[("createdAt", -1)]
    )

    if not timetable_doc:
        raise HTTPException(
            status_code=404,
            detail="No timetable found"
        )


    grade_data = timetable_doc.get("timetable", {}).get(grade)


    if not grade_data:
        raise HTTPException(
            status_code=404,
            detail=f"No timetable found for {grade}"
        )


    result = {}


    for day, periods in grade_data.items():

        result[day] = []


        for period in periods:

            subject = await db["subjects"].find_one(
                {
                    "_id": ObjectId(period["subjectId"])
                }
            )


            teacher = await db["teachers"].find_one(
                {
                    "_id": ObjectId(period["teacherId"])
                }
            )


            result[day].append(
                {
                    "period": period["period"],
                    "subject": subject["subjectName"]
                    if subject else "Unknown",

                    "teacher": teacher["fullName"]
                    if teacher else "Unknown"
                }
            )


    return {
        "grade": grade,
        "days": result
    }