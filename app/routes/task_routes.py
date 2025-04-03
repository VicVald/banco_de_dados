from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.controllers.task_controller import TaskController
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app.database import get_db

router = APIRouter(prefix="/projects", tags=["tasks"])

@router.get("/{project_id}/tasks", response_model=List[TaskResponse])
async def read_project_tasks(project_id: int, db: Session = Depends(get_db)):
    return TaskController.get_project_tasks(db, project_id)

@router.get("/{project_id}/members/{member_id}/tasks", response_model=List[TaskResponse])
async def read_member_tasks(project_id: int, member_id: int, db: Session = Depends(get_db)):
    return TaskController.get_member_tasks(db, project_id, member_id)

@router.post("/{project_id}/tasks", response_model=TaskResponse)
async def create_task(project_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    return TaskController.create_task(db, project_id, task)

@router.put("/{project_id}/members/{member_id}/tasks/{task_number}", response_model=TaskResponse)
async def update_task(
    project_id: int, 
    member_id: int, 
    task_number: int, 
    task_data: TaskUpdate, 
    db: Session = Depends(get_db)
):
    return TaskController.update_task(db, project_id, member_id, task_number, task_data)

@router.delete("/{project_id}/members/{member_id}/tasks/{task_number}")
async def delete_task(project_id: int, member_id: int, task_number: int, db: Session = Depends(get_db)):
    return TaskController.delete_task(db, project_id, member_id, task_number) 