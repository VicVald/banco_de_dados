from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .user_schema import UserResponse

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: int

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectMemberBase(BaseModel):
    user_id: int
    role: str = "sem funcao"

class ProjectMemberCreate(ProjectMemberBase):
    pass

class ProjectMemberUpdate(BaseModel):
    role: Optional[str] = None

class ProjectMemberResponse(BaseModel):
    user: UserResponse
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True

class ProjectResponse(ProjectBase):
    id: int
    owner: UserResponse
    members: List[ProjectMemberResponse]

    class Config:
        from_attributes = True 