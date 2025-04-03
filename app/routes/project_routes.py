from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.controllers.project_controller import ProjectController
from app.schemas.project_schema import ProjectBase, ProjectResponse, ProjectUpdate, ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse
from app.database import get_db

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/{project_id}", response_model=ProjectResponse)
async def read_project(project_id: int, db: Session = Depends(get_db)):
    return ProjectController.get_project(db, project_id)

@router.post("/", response_model=Dict[str, Any])
async def create_project(project: ProjectBase, db: Session = Depends(get_db)):
    return ProjectController.create_project(db, project)

@router.put("/{project_id}", response_model=Dict[str, Any])
async def update_project(project_id: int, project_data: ProjectUpdate, db: Session = Depends(get_db)):
    return ProjectController.update_project(db, project_id, project_data)

@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    return ProjectController.delete_project(db, project_id)

# Rotas para membros do projeto
@router.post("/{project_id}/members", response_model=Dict[str, Any])
async def add_project_member(project_id: int, member: ProjectMemberCreate, db: Session = Depends(get_db)):
    return ProjectController.add_member(db, project_id, member)

@router.put("/{project_id}/members/{member_id}", response_model=ProjectMemberResponse)
async def update_project_member(project_id: int, member_id: int, member_data: ProjectMemberUpdate, db: Session = Depends(get_db)):
    return ProjectController.update_member(db, project_id, member_id, member_data)

@router.delete("/{project_id}/members/{member_id}")
async def delete_project_member(project_id: int, member_id: int, db: Session = Depends(get_db)):
    return ProjectController.delete_member(db, project_id, member_id) 