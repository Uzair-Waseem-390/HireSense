import os
from datetime import datetime
from typing import List
import asyncio 

from fastapi import (
    APIRouter, 
    UploadFile, 
    File, 
    HTTPException, 
    Depends, 
    status,
    BackgroundTasks
)
from sqlalchemy.orm import Session

from database import get_db, SessionLocal
import models
from schemas import resume_schema as schemas
from core.oauth2 import get_current_user
from services.pdf_service import PDFService
from services.agent_service import AgentService
from schemas.agent_schemas import ResumeData
from services.websocket_manager import send_resume_status

router = APIRouter(tags=["Resume"])

UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============ HELPER FUNCTIONS ============
def save_uploaded_file(file_content: bytes, user_id: int, original_filename: str) -> str:
    """Save uploaded file with unique name"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{user_id}_{timestamp}_{original_filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    return file_path

def process_resume_with_agent(resume_id: int, file_path: str, user_id: int):  # ADDED user_id parameter
    """
    Background task: Extract text → AI analysis → Store structured data
    WITH WEBSOCKET UPDATES
    """
    db_bg = SessionLocal()
    
    # Create event loop for async operations
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        resume = db_bg.query(models.Resume).filter(
            models.Resume.resume_id == resume_id
        ).first()
        
        if not resume:
            return
        
        # Step 1: Extract text from PDF
        loop.run_until_complete(send_resume_status(
            user_id=user_id,
            resume_id=resume_id,
            status="extracting",
            message="Extracting text from PDF...",
            progress=25
        ))
        
        resume.status = "extracting"
        db_bg.commit()
        
        extracted_text = PDFService.extract_text_from_pdf(file_path)
        
        loop.run_until_complete(send_resume_status(
            user_id=user_id,
            resume_id=resume_id,
            status="extracting",
            message="Text extracted successfully",
            progress=50,
            data={"text_length": len(extracted_text)}
        ))
        
        # Step 2: Run AI Agent 1 (Resume Analysis)
        loop.run_until_complete(send_resume_status(
            user_id=user_id,
            resume_id=resume_id,
            status="analyzing",
            message="AI is analyzing your resume...",
            progress=60
        ))
        
        resume.status = "analyzing"
        db_bg.commit()
        
        agent_service = AgentService()
        resume_data: ResumeData = agent_service.analyze_resume_with_agent(extracted_text)
        
        loop.run_until_complete(send_resume_status(
            user_id=user_id,
            resume_id=resume_id,
            status="analyzing",
            message="Analysis complete, saving results...",
            progress=90
        ))
        
        # Step 3: Store AI results in database
        resume.text_extracted = extracted_text
        resume.skills = resume_data.skills
        resume.experience = resume_data.experience.model_dump()
        resume.education = resume_data.education
        resume.summary = resume_data.summary
        resume.status = "analyzed"
        
        db_bg.commit()
        
        # Send final success message
        loop.run_until_complete(send_resume_status(
            user_id=user_id,
            resume_id=resume_id,
            status="analyzed",
            message="Resume analysis completed successfully! ✅",
            progress=100,
            data={
                "skills_count": len(resume_data.skills),
                "experience_years": resume_data.experience.total_years,
                "education_count": len(resume_data.education)
            }
        ))
        
        print(f"✅ Resume {resume_id} analyzed successfully")
        
    except Exception as e:
        if resume:
            resume.status = "failed"
            db_bg.commit()
        
        # Send error message via WebSocket
        loop.run_until_complete(send_resume_status(
            user_id=user_id,
            resume_id=resume_id,
            status="failed",
            message=f"Analysis failed: {str(e)}",
            progress=0,
            data={"error": str(e)}
        ))
        
        print(f"❌ Error processing resume {resume_id}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db_bg.close()
        loop.close()

# ============ API ENDPOINTS ============
@router.post("/upload", response_model=schemas.UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF resume file"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a resume PDF for AI analysis with real-time WebSocket updates"""
    # Check for existing active resume
    existing_resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.user_id,
        models.Resume.is_active == True
    ).first()
    
    if existing_resume:
        existing_resume.is_active = False
        db.commit()
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Read and save file
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )
    
    file_path = save_uploaded_file(content, current_user.user_id, file.filename)
    
    # Validate PDF
    is_valid, error_msg = PDFService.validate_pdf(file_path)
    if not is_valid:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Create database record
    db_resume = models.Resume(
        user_id=current_user.user_id,
        filename=file.filename,
        file_path=file_path,
        status="uploaded",
        is_active=True
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    # Send initial WebSocket notification
    await send_resume_status(
        user_id=current_user.user_id,
        resume_id=db_resume.resume_id,
        status="uploaded",
        message="Resume uploaded successfully, starting analysis...",
        progress=10
    )
    
    # Start background processing with user_id
    background_tasks.add_task(
        process_resume_with_agent,
        db_resume.resume_id,
        file_path,
        current_user.user_id  # ADDED this parameter
    )
    
    return {
        "resume_id": db_resume.resume_id,
        "filename": db_resume.filename,
        "message": "Resume uploaded. AI analysis in progress. Connect to WebSocket for real-time updates.",
        "status": "processing"
    }      

@router.get("/my-resume", response_model=schemas.ResumeResponse)
async def get_my_resume(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current active resume with AI analysis"""
    resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.user_id,
        models.Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload your resume first."
        )
    
    if resume.status != "analyzed":
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail=f"Resume is still being processed. Current status: {resume.status}"
        )
    
    return resume

@router.get("/my-resume/analysis")
async def get_resume_analysis(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the AI analysis results in structured format"""
    resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.user_id,
        models.Resume.is_active == True,
        models.Resume.status == "analyzed"
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analyzed resume found"
        )
    
    return {
        "resume_id": resume.resume_id,
        "skills": resume.skills or [],
        "experience": resume.experience or {},
        "education": resume.education or [],
        "summary": resume.summary or "",
        "status": resume.status
    }

@router.get("/me/", response_model=List[schemas.ResumeResponse])
def get_user_resumes(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all resumes uploaded by the authenticated user"""
    resumes = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.user_id
    ).all()
    return resumes

@router.get("/{resume_id}/", response_model=schemas.ResumeResponse)
def get_resume_by_id(
    resume_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific resume by its ID for the authenticated user"""
    resume = db.query(models.Resume).filter(
        models.Resume.resume_id == resume_id,
        models.Resume.user_id == current_user.user_id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found"
        )
    
    return resume

@router.delete("/{resume_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific resume by its ID for the authenticated user"""
    resume_query = db.query(models.Resume).filter(
        models.Resume.resume_id == resume_id,
        models.Resume.user_id == current_user.user_id
    )
    resume = resume_query.first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found"
        )
    
    # Delete the file from filesystem
    if resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {resume.file_path}: {str(e)}")
    
    resume_query.delete(synchronize_session=False)
    db.commit()
    
    return None

@router.put("/{resume_id}/{is_active}", status_code=status.HTTP_200_OK)
def set_resume_active_status(
    resume_id: int,
    is_active: bool,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set the active status of a specific resume for the authenticated user"""
    resume = db.query(models.Resume).filter(
        models.Resume.resume_id == resume_id,
        models.Resume.user_id == current_user.user_id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found"
        )
    
    if is_active:
        # Deactivate all other resumes for this user
        db.query(models.Resume).filter(
            models.Resume.user_id == current_user.user_id,
            models.Resume.resume_id != resume_id
        ).update(
            {models.Resume.is_active: False}, 
            synchronize_session=False
        )
    
    resume.is_active = is_active
    db.commit()
    
    return {
        "message": f"Resume {resume_id} active status set to {is_active}",
        "resume_id": resume_id,
        "is_active": is_active
    }

