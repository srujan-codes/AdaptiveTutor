import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

async def test_generate_quiz_success(client: AsyncClient, test_user: dict, mock_claude):
    # Step 1: Generate a lesson
    mock_claude.send_message.return_value = {
        "title": "Python basics",
        "content": "Intro to python...",
        "key_concepts": ["Vars"],
        "estimated_duration_minutes": 5
    }
    lesson_resp = await client.post(
        "/api/v1/lessons/generate",
        json={"topic": "Python basics", "difficulty": "beginner"},
        headers=test_user["headers"]
    )
    lesson_id = lesson_resp.json()["id"]

    # Step 2: Generate the quiz
    mock_claude.send_message.return_value = {
        "questions": [
            {"question_number": 1, "question_text": "Q1", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "E1"},
            {"question_number": 2, "question_text": "Q2", "options": ["A", "B", "C", "D"], "correct_answer": "B", "explanation": "E2"},
            {"question_number": 3, "question_text": "Q3", "options": ["A", "B", "C", "D"], "correct_answer": "C", "explanation": "E3"},
            {"question_number": 4, "question_text": "Q4", "options": ["A", "B", "C", "D"], "correct_answer": "D", "explanation": "E4"},
            {"question_number": 5, "question_text": "Q5", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "E5"}
        ]
    }
    
    quiz_resp = await client.post(
        "/api/v1/quizzes/generate",
        json={"lesson_id": lesson_id},
        headers=test_user["headers"]
    )
    if quiz_resp.status_code != 200:
        print(quiz_resp.json())
    assert quiz_resp.status_code == 200
    data = quiz_resp.json()
    assert "questions" in data
    assert len(data["questions"]) == 5
    # The endpoint removes correct_answer and explanation before returning
    assert "correct_answer" not in data["questions"][0]
    assert "explanation" not in data["questions"][0]

async def test_submit_quiz_success(client: AsyncClient, test_user: dict, mock_claude):
    # 1. Lesson
    mock_claude.send_message.return_value = {
        "title": "Python", "content": "Py", "key_concepts": ["Py"], "estimated_duration_minutes": 1
    }
    lesson_resp = await client.post("/api/v1/lessons/generate", json={"topic": "Python", "difficulty": "beginner"}, headers=test_user["headers"])
    lesson_id = lesson_resp.json()["id"]

    # 2. Quiz Questions
    mock_claude.send_message.return_value = {
        "questions": [
            {"question_number": 1, "question_text": "Q1", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "E1"},
            {"question_number": 2, "question_text": "Q2", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "E2"},
            {"question_number": 3, "question_text": "Q3", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "E3"},
            {"question_number": 4, "question_text": "Q4", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "E4"},
            {"question_number": 5, "question_text": "Q5", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "E5"}
        ]
    }
    await client.post("/api/v1/quizzes/generate", json={"lesson_id": lesson_id}, headers=test_user["headers"])
    
    # 3. Submit
    # Difficulty adjuster mock
    mock_claude.send_message.return_value = {
        "new_difficulty": "intermediate",
        "reason": "Perfect score"
    }
    
    submit_resp = await client.post(
        "/api/v1/quizzes/submit",
        json={"lesson_id": lesson_id, "answers": ["A", "A", "A", "B", "B"]}, # 3 correct, 2 wrong
        headers=test_user["headers"]
    )
    assert submit_resp.status_code == 200
    submit_data = submit_resp.json()
    assert submit_data["score"] == 3
    assert submit_data["total"] == 5
    assert submit_data["new_difficulty"] == "intermediate"
