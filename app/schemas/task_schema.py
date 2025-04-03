from pydantic import BaseModel
from typing import Optional
from .user_schema import UserResponse
from .project_schema import ProjectResponse

class TaskBase(BaseModel):
    name: str
    description: str
    state: str
    user_id: int
    project_id: int

class TaskCreate(TaskBase):
    pass 

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    user_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    user: UserResponse
    project: ProjectResponse
    task_number: int

    class Config:
        from_attributes = True 