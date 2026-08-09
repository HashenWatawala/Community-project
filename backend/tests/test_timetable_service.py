import pytest
from app.services.timetable_service import generate_and_save_timetable


@pytest.mark.asyncio
async def test_generate_and_save_timetable_uses_ai_function(monkeypatch):
    class DummyDocModel:
        @staticmethod
        async def get_timetable_doc():
            return None

        @staticmethod
        async def save_timetable_doc(payload):
            return {"id": "1", "timetable": payload}

    class DummySubjectModel:
        @staticmethod
        async def list_subjects():
            return [{"id": "sub-1", "grade": 6, "subjectName": "Math", "periodsPerWeek": 5, "assignedTeacher": "teacher-1"}]

    class DummyTeacherModel:
        @staticmethod
        async def list_teachers():
            return [{"id": "teacher-1", "fullName": "Mr. A", "email": "a@example.com", "nicNo": "123", "contactNumber": "000", "hasAssignClass": True, "subjects": []}]

    monkeypatch.setattr("app.services.timetable_service.get_timetable_doc", DummyDocModel.get_timetable_doc)
    monkeypatch.setattr("app.services.timetable_service.save_timetable_doc", DummyDocModel.save_timetable_doc)
    monkeypatch.setattr("app.services.timetable_service.list_subjects", DummySubjectModel.list_subjects)
    monkeypatch.setattr("app.services.timetable_service.list_teachers", DummyTeacherModel.list_teachers)

    async def fake_generate_timetable_from_ai(teachers, subjects):
        return {
            "6A": {"Monday": [{"period": 1, "subjectId": "sub-1", "teacherId": "teacher-1"}]},
        }

    monkeypatch.setattr("app.services.timetable_service.generate_timetable_from_ai", fake_generate_timetable_from_ai)

    class DummyValidator:
        @staticmethod
        def validate_timetable(timetable, subjects, teachers):
            return {"is_valid": True, "errors": []}

    monkeypatch.setattr("app.services.timetable_service.validate_timetable", DummyValidator.validate_timetable)

    result = await generate_and_save_timetable()
    assert result["timetable"]["6A"]["Monday"][0]["subjectId"] == "sub-1"
