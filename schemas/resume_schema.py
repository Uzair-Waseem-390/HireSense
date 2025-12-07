from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ResumeBase(BaseModel):
    filename: Optional[str] = None   # should be Optional
    user_id: Optional[int] = None


class ResumeCreate(ResumeBase):
    pass


class ResumeResponse(ResumeBase):
    resume_id: int
    uploaded_at: datetime
    file_path: Optional[str] = None
    status: str
    text_extracted: Optional[str] = None
    skills: Optional[List[str]] = []
    experience: Optional[Dict[str, Any]] = {}
    education: Optional[List[str]] = []
    summary: Optional[str] = None

    class Config:
        from_attributes = True   # correct for SQLAlchemy objects


class UploadResponse(BaseModel):
    resume_id: int
    filename: str
    message: str
    status: str
