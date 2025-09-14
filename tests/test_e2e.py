import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.v1.mentorship import run_matchmaking_background
from app.core.config import settings
from app.db.database import Base, get_db_session
from app.db.models import SessionStatus, User
from app.main import app
from app.services.session_manager import SessionManager

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
settings.GEMINI_API_KEY = "test_api_key_for_pytest"

async def override_get_db_session():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db_session] = override_get_db_session

@pytest.fixture(scope="function")
async def db_setup_and_teardown():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(db_setup_and_teardown):
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
async def setup_users(client, db_session):
    mentee_data = {"username": "test_mentee", "email": "mentee@test.com", "password": "pw", "role": "mentee", "skills": ["Python"]}
    response_mentee = client.post("/api/v1/users/register", json=mentee_data)
    assert response_mentee.status_code == 201

    mentor_data = {"username": "test_mentor", "email": "mentor@test.com", "password": "pw", "role": "mentor", "skills": ["Python", "AI"]}
    response_mentor = client.post("/api/v1/users/register", json=mentor_data)
    assert response_mentor.status_code == 201

    return {"mentee_id": response_mentee.json()["id"], "mentor_id": response_mentor.json()["id"]}

@pytest.mark.asyncio
@patch('app.agents.orchestrator.MatchmakingOrchestrator.initiate_matchmaking_flow', new_callable=AsyncMock)
async def test_successful_matchmaking_flow(mock_flow, client, db_session, setup_users):
    user_ids = setup_users
    mock_flow.return_value = {"status": "SUCCESS", "mentor_id": user_ids["mentor_id"]}
    request_data = {"user_id": user_ids["mentee_id"], "skill_name": "Python", "request_details": "Help with async"}

    response = client.post("/api/v1/mentorship-requests", json=request_data)
    assert response.status_code == 202
    session_id = response.json()["session_id"]

    await run_matchmaking_background(
        session_id=session_id, user_id=request_data["user_id"],
        skill_name=request_data["skill_name"], request_details=request_data["request_details"],
        db=db_session,
    )

    session = await SessionManager.get_session_by_id(db_session, session_id)
    assert session is not None
    assert session.status == SessionStatus.MATCHED
    assert session.mentor_id == user_ids["mentor_id"]

@pytest.mark.asyncio
@patch('app.agents.orchestrator.MatchmakingOrchestrator.initiate_matchmaking_flow', new_callable=AsyncMock)
async def test_failed_matchmaking_due_to_low_trust(mock_flow, client, db_session, setup_users):
    user_ids = setup_users
    mentee = await db_session.get(User, user_ids["mentee_id"])
    mentee.trust_score = 10.0
    await db_session.commit()
    mock_flow.return_value = {"status": "FAILED", "reason": "User trust score is below the 30 point threshold."}
    request_data = {"user_id": user_ids["mentee_id"], "skill_name": "Python", "request_details": "Test low trust"}

    response = client.post("/api/v1/mentorship-requests", json=request_data)
    assert response.status_code == 202
    session_id = response.json()["session_id"]

    await run_matchmaking_background(
        session_id=session_id, user_id=request_data["user_id"],
        skill_name=request_data["skill_name"], request_details=request_data["request_details"],
        db=db_session,
    )

    session = await SessionManager.get_session_by_id(db_session, session_id)
    assert session is not None
    assert session.status == SessionStatus.FAILED
    assert "trust score" in session.failure_reason