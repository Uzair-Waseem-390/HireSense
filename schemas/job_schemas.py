# schemas/job_schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request schemas
class JobDescriptionCreate(BaseModel):
    title: Optional[str] = Field(None, description="Job title (optional)")
    description: str = Field(..., description="Full job description text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Python Developer",
                "description": "We are looking for a Python developer with 5+ years experience..."
            }
        }

class MatchJobRequest(BaseModel):
    job_description: str = Field(..., description="Job description to match against")
    title: Optional[str] = Field(None, description="Job title (optional)")
    resume_id: Optional[int] = Field(None, description="Resume ID to use (defaults to active resume)")

# Response schemas
class JobDescriptionResponse(BaseModel):
    job_id: int
    user_id: int
    title: Optional[str]
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobMatchResponse(BaseModel):
    match_id: int
    resume_id: int
    job_id: int
    user_id: int
    fit_score: Optional[int]
    strengths: Optional[List[str]]
    missing_skills: Optional[List[str]]
    recommendations: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobMatchDetailResponse(BaseModel):
    match_id: int
    fit_score: int
    strengths: List[str]
    missing_skills: List[str]
    recommendations: str
    created_at: datetime
    job: Dict[str, Any]
    resume_skills: List[str]
    
class MatchStatusResponse(BaseModel):
    message: str
    job_id: int
    resume_id: int
    status: str