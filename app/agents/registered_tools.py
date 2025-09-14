import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db import models

async def verify_user_trust(user_id: int, db: AsyncSession) -> str:
    """Verifies if a user's trust score meets the required threshold."""
    query = select(models.User).where(models.User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None:
        return json.dumps({"user_id": user_id, "status": "NOT_FOUND", "details": "User does not exist."})
    
    if user.trust_score < 30.0:
        return json.dumps({"user_id": user_id, "status": "UNTRUSTWORTHY", "score": user.trust_score, "details": "User trust score is below the 30 point threshold."})
    
    return json.dumps({"user_id": user_id, "status": "VERIFIED", "score": user.trust_score, "details": "User is verified and in good standing."})

async def find_potential_mentors(skill_name: str, db: AsyncSession) -> str:
    """Finds suitable mentors for a given skill, prioritizing higher trust scores."""
    query = (
        select(models.User)
        .options(selectinload(models.User.skills))
        .join(models.User.skills)
        .where(
            models.Skill.name.ilike(f"%{skill_name}%"),
            models.User.role.in_([models.UserRole.MENTOR, models.UserRole.BOTH]),
            models.User.trust_score > 50
        )
        .order_by(models.User.trust_score.desc())
        .limit(10)
    )
    
    result = await db.execute(query)
    mentors = result.scalars().unique().all()
    
    mentor_data = [
        {"id": mentor.id, "username": mentor.username, "trust_score": mentor.trust_score}
        for mentor in mentors
    ]
    
    return json.dumps({"skill_name": skill_name, "mentors": mentor_data})

async def save_session_summary(session_id: int, summary_text: str, db: AsyncSession) -> str:
    """Saves the generated summary and marks the mentorship session as completed."""
    query = select(models.MentorshipSession).where(models.MentorshipSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if session:
        session.summary = summary_text
        session.status = models.SessionStatus.COMPLETED
        await db.commit()
        return json.dumps({"session_id": session_id, "status": "SUCCESS", "details": "Summary saved and session marked as COMPLETED."})
    else:
        return json.dumps({"session_id": session_id, "status": "ERROR", "details": "Session not found."})