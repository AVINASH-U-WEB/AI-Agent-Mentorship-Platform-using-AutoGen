import traceback
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import MatchmakingOrchestrator
from app.db.database import AsyncSessionLocal, get_db_session
from app.services.session_manager import SessionManager

router = APIRouter()

class MentorshipRequest(BaseModel):
    user_id: int
    skill_name: str
    request_details: str

@asynccontextmanager
async def get_task_db_session(
    db_session: AsyncSession | None,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager that yields the provided session for tests,
    or creates a new one for normal operation.
    """
    if db_session:
        yield db_session
    else:
        async with AsyncSessionLocal() as new_session:
            yield new_session

async def run_matchmaking_background(
    session_id: int,
    user_id: int,
    skill_name: str,
    request_details: str,
    db: AsyncSession | None = None,
):
    """
    Runs the AI agent matchmaking flow. It can now operate using a provided DB session for testing.
    """
    async with get_task_db_session(db) as db_session:
        print(f"\n--- ✅ BACKGROUND TASK STARTED for session_id: {session_id} ---")
        try:
            orchestrator = MatchmakingOrchestrator(db_session=db_session)
            result = await orchestrator.initiate_matchmaking_flow(
                user_id=user_id,
                skill_name=skill_name,
                request_details=request_details,
            )
            print(f"--- 🏁 AI AGENTS FINISHED. RAW RESULT: {result} ---")

            if result and result.get("status") == "SUCCESS":
                mentor_id = result.get("mentor_id")
                await SessionManager.assign_mentor_to_session(db_session, session_id, mentor_id)
            else:
                reason = result.get("reason", "No reason provided.")
                await SessionManager.mark_session_failed(db_session, session_id, reason)

        except Exception:
            traceback.print_exc()
            await SessionManager.mark_session_failed(
                db_session, session_id, "An unexpected internal error occurred."
            )
        finally:
            print(f"--- ⏹️ BACKGROUND TASK FINISHED for session_id: {session_id} ---\n")

@router.post("/mentorship-requests", status_code=202)
async def request_mentorship(
    request: MentorshipRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
):
    skill = await SessionManager.get_skill_by_name(db, request.skill_name)
    if not skill:
        raise HTTPException(
            status_code=404, detail=f"Skill '{request.skill_name}' not found."
        )

    session = await SessionManager.create_session_request(db, request.user_id, skill.id)
    
    background_tasks.add_task(
        run_matchmaking_background,
        session.id,
        request.user_id,
        request.skill_name,
        request.request_details,
    )

    return {
        "message": "Matchmaking request received and is being processed.",
        "session_id": session.id,
    }