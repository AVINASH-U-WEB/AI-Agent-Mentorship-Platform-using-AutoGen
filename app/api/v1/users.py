from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
# --- FIX: Import selectinload for eager loading ---
from sqlalchemy.orm import selectinload

from app.db.database import get_db_session
from app.db.models import User, UserRole, Skill
from app.core.security import Hasher

router = APIRouter()

class SkillOut(BaseModel):
    id: int
    name: str
    domain: str | None
    class Config: from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.MENTEE
    skills: List[str] = []

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    skills: List[SkillOut] = []
    class Config: from_attributes = True

@router.post("/users/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=Hasher.get_password_hash(user_data.password),
        role=user_data.role
    )

    if user_data.skills:
        for skill_name in user_data.skills:
            result = await db.execute(select(Skill).where(Skill.name.ilike(skill_name)))
            skill = result.scalar_one_or_none()
            if not skill:
                skill = Skill(name=skill_name.strip(), domain="Uncategorized")
                db.add(skill)
                await db.flush()
            new_user.skills.append(skill)
            
    db.add(new_user)
    try:
        await db.commit()
        
        # --- FIX: Eagerly load the 'skills' relationship before returning ---
        # We re-fetch the user with the skills pre-loaded to prevent lazy loading during serialization.
        result = await db.execute(
            select(User).options(selectinload(User.skills)).where(User.id == new_user.id)
        )
        final_user = result.scalar_one()
        return final_user

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists."
        )