from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
from core.security import hash_password
from schemas import user_schema
from core import oauth2

router = APIRouter(tags=["Users"])

# Create a new user
@router.post("/register/", status_code=status.HTTP_201_CREATED, response_model=user_schema.UserResponse)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user.email} already exists"
        )
    # Hash the password before storing
    hashed_password = hash_password(user.password)
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_password,
        admin=user.admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Update a user
@router.put("/user/{user_id}", status_code=status.HTTP_200_OK)
def update_user(user_id: int, updated_user: user_schema.UserUpdate, db: Session = Depends(get_db)):
    # if current_user.user_id != user_id and not current_user.admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to update this user"
    #     )
    
    user_query = db.query(models.User).filter(models.User.user_id == user_id)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Hash password if it's being updated
    update_data = updated_user.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )
    
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    
    if "admin" not in update_data:
        update_data["admin"] = user.admin
        

    user_query.update(update_data, synchronize_session=False)
    db.commit()
    return {"message": "User updated", "user": user_query.first()}


# Get all users
@router.get("/users/", response_model=List[user_schema.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


# Get a single user by ID
@router.get("/user/{user_id}", response_model=user_schema.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


# Delete a user
@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.user_id == user_id)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    user_query.delete(synchronize_session=False)
    db.commit()
    return {"message": "User deleted"}

# untested route to get current user profile
@router.get("/users/profile", status_code=status.HTTP_200_OK)
def get_user_profile(current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user