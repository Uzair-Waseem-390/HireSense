from pydantic import BaseModel, Field
from typing import List, Optional, Annotated

class Position(BaseModel):
    title: str = Field(..., description="The job title held by the person.")
    company: str = Field(..., description="The name of the company or organization.")
    years: str = Field(..., description="The duration of the employment.")

class Experience(BaseModel):
    total_years: Optional[float] = Field(None, description="Total years of professional experience.")
    positions: List[Position] = Field(..., description="Array of specific positions held.")

class ResumeData(BaseModel):
    skills: Annotated[List[str], Field(max_length=15)] = Field(
        ..., 
        description="Technical/professional skills (max 15 items)."
    )
    experience: Experience = Field(..., description="Professional work experience.")
    education: List[str] = Field(..., description="Educational degrees or certifications.")
    summary: str = Field(..., description="Brief professional summary (2-3 sentences).")

class JobMatchData(BaseModel):
    fit_score: Annotated[int, Field(ge=0, le=100)] = Field(
        ..., description="Match score (0-100)."
    )
    strengths: Annotated[List[str], Field(min_length=3, max_length=5)] = Field(
        ..., description="3-5 strongest matches."
    )
    missing_skills: Annotated[List[str], Field(min_length=3, max_length=5)] = Field(
        ..., description="3-5 missing but required skills."
    )
    recommendations: Annotated[List[str], Field(min_length=2, max_length=3)] = Field(
        ..., description="2-3 actionable recommendations."
    )