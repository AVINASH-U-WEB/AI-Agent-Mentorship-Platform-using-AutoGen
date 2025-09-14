# app/db/models.py
import enum
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey, Enum as SAEnum, Float, Table
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class UserRole(enum.Enum):
    MENTOR = "mentor"
    MENTEE = "mentee"
    BOTH = "both"

class SessionStatus(enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Association table for the many-to-many relationship between users and skills
user_skills_association = Table(
    'user_skills', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.MENTEE)
    trust_score = Column(Float, default=50.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    skills = relationship("Skill", secondary=user_skills_association, back_populates="users")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    domain = Column(String)
    users = relationship("User", secondary=user_skills_association, back_populates="skills")

class MentorshipSession(Base):
    __tablename__ = "mentorship_sessions"
    id = Column(Integer, primary_key=True, index=True)
    mentee_id = Column(Integer, ForeignKey("users.id"))
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    requested_skill_id = Column(Integer, ForeignKey("skills.id"))
    status = Column(SAEnum(SessionStatus), default=SessionStatus.PENDING)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)

    mentee = relationship("User", foreign_keys=[mentee_id])
    mentor = relationship("User", foreign_keys=[mentor_id])
    skill = relationship("Skill", foreign_keys=[requested_skill_id])