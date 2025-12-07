from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends, 
    status,
    security
)
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from database import get_db, SessionLocal
import models
from core.oauth2 import get_current_user
from schemas import user_schema, resume_schema, job_schemas
from fastapi import Security


router = APIRouter(tags=["Admin"])

def admin_required(current_user: models.User = Depends(get_current_user)):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.get("/users", response_model=List[user_schema.UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(skip: int = 0, limit: int = 100,
                        db: Session = Depends(get_db),
                        current_user: models.User = Depends(admin_required)):
    """Admin: List all users"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/resumes", response_model=List[resume_schema.ResumeResponse], status_code=status.HTTP_200_OK)
async def get_all_resumes(skip: int = 0, limit: int = 100,
                          db: Session = Depends(get_db),
                          current_user: models.User = Depends(admin_required)):
    """Admin: List all resumes"""
    resumes = db.query(models.Resume).offset(skip).limit(limit).all()
    return resumes

@router.get("/matches", response_model=List[job_schemas.JobMatchResponse], status_code=status.HTTP_200_OK)
async def get_all_matches(skip: int = 0, limit: int = 100,
                          db: Session = Depends(get_db),
                          current_user: models.User = Depends(admin_required)):
    """Admin: List all job matches"""
    matches = db.query(models.JobMatch).offset(skip).limit(limit).all()
    return matches

@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_required)
):
    """Admin: Get platform statistics and calculations"""
    total_users = db.query(models.User).count()
    total_resumes = db.query(models.Resume).count()
    total_matches = db.query(models.JobMatch).count()
    total_jobs = db.query(models.JobDescription).count()
    
    # Average fit score
    avg_fit_score = db.query(func.avg(models.JobMatch.fit_score)).filter(
        models.JobMatch.fit_score.isnot(None)
    ).scalar()
    
    # Users with resumes
    users_with_resumes = db.query(func.count(func.distinct(models.Resume.user_id))).scalar()
    
    # Active resumes count
    active_resumes = db.query(models.Resume).filter(models.Resume.is_active == True).count()
    
    # Resume status breakdown
    resume_statuses = db.query(
        models.Resume.status,
        func.count(models.Resume.resume_id)
    ).group_by(models.Resume.status).all()
    
    status_breakdown = {status: count for status, count in resume_statuses}
    
    # Average matches per user
    avg_matches_per_user = total_matches / total_users if total_users > 0 else 0
    
    return {
        "total_users": total_users,
        "total_resumes": total_resumes,
        "total_matches": total_matches,
        "total_jobs": total_jobs,
        "average_fit_score": round(float(avg_fit_score), 2) if avg_fit_score else 0,
        "users_with_resumes": users_with_resumes,
        "active_resumes": active_resumes,
        "resume_status_breakdown": status_breakdown,
        "average_matches_per_user": round(float(avg_matches_per_user), 2)
    }