from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    Boolean, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from datetime import datetime
from database import Base



class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    admin = Column(Boolean, default=False)

    # Relationships
    resumes = relationship("Resume", back_populates="user")
    job_descriptions = relationship("JobDescription", back_populates="user")
    job_matches = relationship("JobMatch", back_populates="user")



class Resume(Base):
    __tablename__ = "resumes"

    resume_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    filename = Column(String)
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    text_extracted = Column(Text)
    skills = Column(JSON, default=[])
    experience = Column(JSON, default={})
    education = Column(JSON, default=[])
    summary = Column(Text)

    is_active = Column(Boolean, default=True)
    status = Column(String, default="uploaded")

    # Relationship
    user = relationship("User", back_populates="resumes")
    job_matches = relationship("JobMatch", back_populates="resume")
    
    def get_resume_data_dict(self):
        """Convert to dictionary format for AI agent"""
        return {
            "skills": self.skills or [],
            "experience": self.experience or {},
            "education": self.education or [],
            "summary": self.summary or ""
        }


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    job_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    title = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="job_descriptions")
    job_matches = relationship("JobMatch", back_populates="job_description")


class JobMatch(Base):
    __tablename__ = "job_matches"

    match_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    resume_id = Column(Integer, ForeignKey("resumes.resume_id"))
    job_id = Column(Integer, ForeignKey("job_descriptions.job_id"))

    fit_score = Column(Integer)
    strengths = Column(JSON, default=[])
    missing_skills = Column(JSON, default=[])
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="job_matches")
    resume = relationship("Resume", back_populates="job_matches")
    job_description = relationship("JobDescription", back_populates="job_matches")
