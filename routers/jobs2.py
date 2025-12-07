import json
from typing import List, Optional
from datetime import datetime

from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends, 
    status,
    BackgroundTasks,
    Query
)
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from database import get_db, SessionLocal
import models
from schemas import job_schemas as schemas
from core.oauth2 import get_current_user
from services.agent_service import AgentService  # Changed from agent_service2
from schemas.agent_schemas import ResumeData, JobMatchData, Experience, Position

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# ============ HELPER FUNCTIONS ============
def process_job_match(
    resume_id: int, 
    job_id: int, 
    job_description: str,
    resume_skills: List[str],
    resume_experience: dict,
    resume_education: List[str],
    resume_summary: str
):
    """
    Background task: Run AI job matching agent
    """
    db_bg = SessionLocal()
    
    try:
        # Get resume and job from database
        resume = db_bg.query(models.Resume).filter(
            models.Resume.resume_id == resume_id
        ).first()
        
        job = db_bg.query(models.JobDescription).filter(
            models.JobDescription.job_id == job_id
        ).first()
        
        if not resume or not job:
            print(f"❌ Resume {resume_id} or Job {job_id} not found")
            return
        
        # Parse experience properly
        try:
            if isinstance(resume_experience, dict):
                experience = Experience(
                    total_years=resume_experience.get("total_years", 0),
                    positions=[
                        Position(**pos) if isinstance(pos, dict) else pos
                        for pos in resume_experience.get("positions", [])
                    ]
                )
            else:
                experience = Experience(total_years=0, positions=[])
        except Exception as e:
            print(f"⚠️ Error parsing experience: {e}")
            experience = Experience(total_years=0, positions=[])
        
        # Prepare ResumeData object for agent
        resume_data = ResumeData(
            skills=resume_skills or [],
            experience=experience,
            education=resume_education or [],
            summary=resume_summary or ""
        )
        
        # Run AI Agent 2 (Job Matcher)
        print(f"🤖 Starting AI job matching for resume {resume_id}, job {job_id}")
        agent_service = AgentService()
        match_result: JobMatchData = agent_service.analyze_job_fit_with_agent(
            job_description=job_description,
            resume_data=resume_data
        )
        
        # Save match results
        job_match = models.JobMatch(
            user_id=resume.user_id,
            resume_id=resume_id,
            job_id=job_id,
            fit_score=match_result.fit_score,
            strengths=match_result.strengths,
            missing_skills=match_result.missing_skills,
            recommendations="\n".join(match_result.recommendations)
        )
        db_bg.add(job_match)
        db_bg.commit()
        
        print(f"✅ Job match completed successfully")
        print(f"   Fit Score: {match_result.fit_score}")
        print(f"   Match ID: {job_match.match_id}")
        
    except Exception as e:
        print(f"❌ Error in job matching: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db_bg.close()

# ============ API ENDPOINTS ============

@router.post("/match", 
             response_model=schemas.MatchStatusResponse, 
             status_code=status.HTTP_202_ACCEPTED)
async def match_job(
    match_request: schemas.MatchJobRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a job description for AI-powered matching
    
    - If resume_id is provided, use that resume
    - Otherwise, use user's active resume
    - Triggers AI matching in background
    """
    # Determine which resume to use
    if match_request.resume_id:
        # Use specified resume
        resume = db.query(models.Resume).filter(
            models.Resume.resume_id == match_request.resume_id,
            models.Resume.user_id == current_user.user_id
        ).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {match_request.resume_id} not found"
            )
    else:
        # Use active resume
        resume = db.query(models.Resume).filter(
            models.Resume.user_id == current_user.user_id,
            models.Resume.is_active == True
        ).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active resume found. Please upload a resume first."
            )
    
    # Check if resume is analyzed
    if resume.status != "analyzed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume is not analyzed yet. Current status: {resume.status}"
        )
    
    # Save job description
    job_desc = models.JobDescription(
        user_id=current_user.user_id,
        title=match_request.title,
        description=match_request.job_description
    )
    db.add(job_desc)
    db.commit()
    db.refresh(job_desc)
    
    # Start background matching task
    background_tasks.add_task(
        process_job_match,
        resume.resume_id,
        job_desc.job_id,
        match_request.job_description,
        resume.skills,
        resume.experience,
        resume.education,
        resume.summary
    )
    
    return {
        "message": "Job matching started. Results will be available shortly.",
        "job_id": job_desc.job_id,
        "resume_id": resume.resume_id,
        "status": "processing"
    }

@router.get("/matches", response_model=List[schemas.JobMatchResponse])
async def get_my_matches(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Number of matches to return"),
    offset: int = Query(0, ge=0, description="Number of matches to skip")
):
    """
    Get all job matches for current user (paginated)
    """
    matches = db.query(models.JobMatch).join(models.Resume).filter(
        models.Resume.user_id == current_user.user_id
    ).order_by(desc(models.JobMatch.created_at)).offset(offset).limit(limit).all()
    
    return matches

@router.get("/matches/{match_id}", response_model=schemas.JobMatchDetailResponse)
async def get_match_detail(
    match_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed match result with full context
    """
    match = db.query(models.JobMatch).join(models.Resume).filter(
        models.JobMatch.match_id == match_id,
        models.Resume.user_id == current_user.user_id
    ).first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Get associated job description
    job = db.query(models.JobDescription).filter(
        models.JobDescription.job_id == match.job_id
    ).first()
    
    # Get resume skills
    resume = db.query(models.Resume).filter(
        models.Resume.resume_id == match.resume_id
    ).first()
    
    return {
        "match_id": match.match_id,
        "fit_score": match.fit_score or 0,
        "strengths": match.strengths or [],
        "missing_skills": match.missing_skills or [],
        "recommendations": match.recommendations or "",
        "created_at": match.created_at,
        "job": {
            "job_id": job.job_id if job else None,
            "title": job.title if job else None,
            "description": job.description if job else None,
            "created_at": job.created_at if job else None
        },
        "resume_skills": resume.skills if resume else []
    }

@router.post("/quick-match")
async def quick_match(
    match_request: schemas.MatchJobRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick match - returns immediate results without saving to database
    (Good for testing or quick comparisons)
    """
    # Get resume (active or specified)
    if match_request.resume_id:
        resume = db.query(models.Resume).filter(
            models.Resume.resume_id == match_request.resume_id,
            models.Resume.user_id == current_user.user_id
        ).first()
    else:
        resume = db.query(models.Resume).filter(
            models.Resume.user_id == current_user.user_id,
            models.Resume.is_active == True
        ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found"
        )
    
    if resume.status != "analyzed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume is not analyzed yet. Status: {resume.status}"
        )
    
    # Parse experience properly
    try:
        if isinstance(resume.experience, dict):
            experience = Experience(
                total_years=resume.experience.get("total_years", 0),
                positions=[
                    Position(**pos) if isinstance(pos, dict) else pos
                    for pos in resume.experience.get("positions", [])
                ]
            )
        else:
            experience = Experience(total_years=0, positions=[])
    except Exception as e:
        print(f"⚠️ Error parsing experience: {e}")
        experience = Experience(total_years=0, positions=[])
    
    # Prepare resume data
    resume_data = ResumeData(
        skills=resume.skills or [],
        experience=experience,
        education=resume.education or [],
        summary=resume.summary or ""
    )
    
    # Run agent synchronously (for quick response)
    try:
        agent_service = AgentService()
        match_result: JobMatchData = await run_in_threadpool(
        agent_service.analyze_job_fit_with_agent,
        match_request.job_description,
        resume_data
        )
        # match_result: JobMatchData = agent_service.analyze_job_fit_with_agent(
        #     job_description=match_request.job_description,
        #     resume_data=resume_data
        # )
        
        return {
            "fit_score": match_result.fit_score,
            "strengths": match_result.strengths,
            "missing_skills": match_result.missing_skills,
            "recommendations": match_result.recommendations,
            "instant_match": True,
            "resume_id": resume.resume_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI matching failed: {str(e)}"
        )

@router.get("/descriptions", response_model=List[schemas.JobDescriptionResponse])
async def get_my_job_descriptions(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all job descriptions submitted by user
    """
    jobs = db.query(models.JobDescription).filter(
        models.JobDescription.user_id == current_user.user_id
    ).order_by(desc(models.JobDescription.created_at)).all()
    
    return jobs

@router.get("/descriptions/{job_id}", response_model=schemas.JobDescriptionResponse)
async def get_job_description(
    job_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific job description
    """
    job = db.query(models.JobDescription).filter(
        models.JobDescription.job_id == job_id,
        models.JobDescription.user_id == current_user.user_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    return job

@router.delete("/matches/{match_id}", status_code=status.HTTP_200_OK)
async def delete_match(
    match_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific match result
    """
    match = db.query(models.JobMatch).join(models.Resume).filter(
        models.JobMatch.match_id == match_id,
        models.Resume.user_id == current_user.user_id
    ).first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    db.delete(match)
    db.commit()
    
    return {"message": "Match deleted successfully"}

@router.get("/stats")
async def get_job_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get job matching statistics for the user
    """
    total_matches = db.query(models.JobMatch).join(models.Resume).filter(
        models.Resume.user_id == current_user.user_id
    ).count()
    
    total_jobs = db.query(models.JobDescription).filter(
        models.JobDescription.user_id == current_user.user_id
    ).count()
    
    # Get average fit score (FIXED)
    avg_score_result = db.query(func.avg(models.JobMatch.fit_score)).join(models.Resume).filter(
        models.Resume.user_id == current_user.user_id,
        models.JobMatch.fit_score.isnot(None)
    ).scalar()
    
    # Get active resume
    active_resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.user_id,
        models.Resume.is_active == True
    ).first()
    
    return {
        "total_matches": total_matches,
        "total_jobs": total_jobs,
        "average_fit_score": round(float(avg_score_result), 2) if avg_score_result else 0,
        "active_resume": active_resume.filename if active_resume else None
    }