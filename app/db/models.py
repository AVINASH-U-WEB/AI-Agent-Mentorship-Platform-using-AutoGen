import enum
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey, Enum as SAEnum, Float, Table
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class UserRole(str, enum.Enum):
    MENTOR = "mentor"
    MENTEE = "mentee"
    BOTH = "both"

class SessionStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

user_skills_association = Table(
    'user_skills', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.MENTEE, nullable=False)
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
    mentee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    requested_skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    status = Column(SAEnum(SessionStatus), default=SessionStatus.PENDING, nullable=False)
    failure_reason = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)

    mentee = relationship("User", foreign_keys=[mentee_id])
    mentor = relationship("User", foreign_keys=[mentor_id])
    skill = relationship("Skill", foreign_keys=[requested_skill_id])