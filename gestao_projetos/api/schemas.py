"""
Esquemas para validação e serialização de dados na API
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    """Esquema base para usuários."""
    name: str = Field(..., description="Nome do usuário", min_length=2, max_length=100)
    email: EmailStr = Field(..., description="Email do usuário")


class UserCreate(UserBase):
    """Esquema para criação de usuários."""
    pass


class UserUpdate(BaseModel):
    """Esquema para atualização de usuários."""
    name: Optional[str] = Field(None, description="Nome do usuário", min_length=2, max_length=100)
    email: Optional[EmailStr] = Field(None, description="Email do usuário")
    is_active: Optional[bool] = Field(None, description="Status de ativação do usuário")


class UserResponse(UserBase):
    """Esquema para resposta de usuários."""
    id: int = Field(..., description="ID do usuário")
    is_active: bool = Field(..., description="Status de ativação do usuário")

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Esquema base para projetos."""
    name: str = Field(..., description="Nome do projeto", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Descrição do projeto")


class ProjectCreate(ProjectBase):
    """Esquema para criação de projetos."""
    owner_id: int = Field(..., description="ID do usuário dono do projeto")


class ProjectUpdate(BaseModel):
    """Esquema para atualização de projetos."""
    name: Optional[str] = Field(None, description="Nome do projeto", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Descrição do projeto")


class ProjectMemberBase(BaseModel):
    """Esquema base para membros de projeto."""
    user_id: int = Field(..., description="ID do usuário membro")
    role: str = Field("membro", description="Papel do usuário no projeto")


class ProjectMemberCreate(ProjectMemberBase):
    """Esquema para adição de membros ao projeto."""
    pass


class ProjectMemberUpdate(BaseModel):
    """Esquema para atualização de membros de projeto."""
    role: Optional[str] = Field(None, description="Papel do usuário no projeto")


class ProjectMemberResponse(BaseModel):
    """Esquema para resposta de membros de projeto."""
    user_id: int = Field(..., description="ID do usuário membro")
    project_id: int = Field(..., description="ID do projeto")
    role: str = Field(..., description="Papel do usuário no projeto")
    joined_at: datetime = Field(..., description="Data de entrada no projeto")
    user: Optional[UserResponse] = Field(None, description="Dados do usuário")

    class Config:
        from_attributes = True


class ProjectResponse(ProjectBase):
    """Esquema para resposta de projetos."""
    id: int = Field(..., description="ID do projeto")
    created_at: datetime = Field(..., description="Data de criação do projeto")
    owner_id: int = Field(..., description="ID do usuário dono do projeto")
    owner: Optional[UserResponse] = Field(None, description="Dados do usuário dono")
    members: List[ProjectMemberResponse] = Field([], description="Membros do projeto")

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    """Esquema base para tarefas."""
    title: str = Field(..., description="Título da tarefa", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Descrição da tarefa")
    state: str = Field("backlog", description="Estado da tarefa")


class TaskCreate(TaskBase):
    """Esquema para criação de tarefas."""
    project_id: int = Field(..., description="ID do projeto")
    user_id: Optional[int] = Field(None, description="ID do usuário atribuído à tarefa")


class TaskUpdate(BaseModel):
    """Esquema para atualização de tarefas."""
    title: Optional[str] = Field(None, description="Título da tarefa", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Descrição da tarefa")
    state: Optional[str] = Field(None, description="Estado da tarefa")
    user_id: Optional[int] = Field(None, description="ID do usuário atribuído à tarefa")


class TaskAssign(BaseModel):
    """Esquema para atribuição de tarefa."""
    user_id: Optional[int] = Field(None, description="ID do usuário atribuído à tarefa")


class TaskChangeState(BaseModel):
    """Esquema para mudança de estado de tarefa."""
    state: str = Field(..., description="Novo estado da tarefa")


class TaskResponse(TaskBase):
    """Esquema para resposta de tarefas."""
    id: int = Field(..., description="ID da tarefa")
    task_number: int = Field(..., description="Número da tarefa dentro do projeto")
    project_id: int = Field(..., description="ID do projeto")
    user_id: Optional[int] = Field(None, description="ID do usuário atribuído à tarefa")
    created_at: datetime = Field(..., description="Data de criação da tarefa")
    updated_at: datetime = Field(..., description="Data da última atualização da tarefa")
    assigned_user: Optional[UserResponse] = Field(None, description="Dados do usuário atribuído")
    project: Optional[ProjectResponse] = Field(None, description="Dados do projeto")

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Esquema para resposta de erro."""
    detail: str = Field(..., description="Mensagem de erro")
    status_code: int = Field(..., description="Código de status HTTP")
    error_type: Optional[str] = Field(None, description="Tipo de erro") 