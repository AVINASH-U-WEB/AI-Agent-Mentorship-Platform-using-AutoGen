from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import models

class SessionManager:
    @staticmethod
    async def get_session_by_id(db: AsyncSession, session_id: int) -> models.MentorshipSession | None:
        """Retrieves a single session by its ID."""
        result = await db.execute(select(models.MentorshipSession).where(models.MentorshipSession.id == session_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_session_request(db: AsyncSession, mentee_id: int, skill_id: int) -> models.MentorshipSession:
        """Creates a new mentorship session with a 'PENDING' status."""
        new_session = models.MentorshipSession(
            mentee_id=mentee_id,
            requested_skill_id=skill_id,
            status=models.SessionStatus.PENDING
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        return new_session

    @staticmethod
    async def assign_mentor_to_session(db: AsyncSession, session_id: int, mentor_id: int) -> models.MentorshipSession | None:
        """Assigns a mentor to a session and updates its status to 'MATCHED'."""
        session = await SessionManager.get_session_by_id(db, session_id)
        if session:
            session.mentor_id = mentor_id
            session.status = models.SessionStatus.MATCHED
            await db.commit()
            await db.refresh(session)
            return session
        return None

    @staticmethod
    async def mark_session_failed(db: AsyncSession, session_id: int, reason: str) -> models.MentorshipSession | None:
        """Updates a session's status to 'FAILED' and records the reason."""
        session = await SessionManager.get_session_by_id(db, session_id)
        if session:
            session.status = models.SessionStatus.FAILED
            session.failure_reason = reason
            await db.commit()
            await db.refresh(session)
            return session
        return None

    # --- THIS IS THE CORRECTED METHOD ---
    # The indentation has been fixed to align it with the other methods in the class.
    @staticmethod
    async def get_skill_by_name(db: AsyncSession, skill_name: str) -> models.Skill | None:
        """Retrieves a skill by its name (case-insensitive)."""
        result = await db.execute(select(models.Skill).where(models.Skill.name.ilike(skill_name)))
        return result.scalar_one_or_none()