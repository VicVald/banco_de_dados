from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.controllers.user_controller import UserController
from app.schemas.user_schema import UserBase, UserResponse, UserUpdate
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def read_users(db: Session = Depends(get_db)):
    return UserController.get_users(db)

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    return UserController.get_user_by_id(db, user_id)

@router.post("/", response_model=UserResponse)
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    return UserController.create_user(db, user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    return UserController.update_user(db, user_id, user_data)

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    return UserController.delete_user(db, user_id) 