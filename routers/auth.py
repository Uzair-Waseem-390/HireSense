from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db
import models
from core import oauth2
from core.security import verify_password
from schemas import token_schema, user_schema


router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=token_schema.Token)
async def login(user_credentials: user_schema.UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )

    # Verify password
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )

    # Create JWT token with correct user_id
    access_token = oauth2.create_access_token(data={"user_id": user.user_id})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=user_schema.UserResponse)
async def get_current_user_details(current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user