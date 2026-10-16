import pytest
import os
import database
from database import init_db, create_user, verify_user
from quiz_agent import grade_answers


@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup: point the database module itself at a throwaway test file,
    # so tests never touch your real lumo.db.
    database.DB_FILE = "test_lumo.db"
    init_db()
    yield
    # Teardown
    database.DB_FILE = "lumo.db"
    if os.path.exists("test_lumo.db"):
        os.remove("test_lumo.db")


def test_auth_flow():
    # Test Signup
    uid = create_user("testuser", "password123")
    assert uid is not None
    # Test duplicate prevention
    assert create_user("testuser", "newpass") is None
    # Test Login
    assert verify_user("testuser", "password123") == uid
    assert verify_user("testuser", "wrongpass") is None


def test_quiz_grading():
    q = [{"correct_index": 1}, {"correct_index": 2}]
    result = grade_answers(q, [1, 0])  # 1 correct, 1 wrong
    assert result["score"] == 1
    assert result["total"] == 2
    assert result["weak"] == True
