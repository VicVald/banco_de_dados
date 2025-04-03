"""
Rotas da API para projetos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List

from gestao_projetos.api.schemas import (
    ProjectCreate, 
    ProjectUpdate, 
    ProjectResponse, 
    ProjectMemberCreate,
    ProjectMemberUpdate,
    ProjectMemberResponse,
    ErrorResponse
)
from gestao_projetos.controllers.project_controller import ProjectController
from gestao_projetos.core.database import get_db
from gestao_projetos.core.exceptions import (
    ResourceNotFoundException,
    NotProjectOwnerError,
    AlreadyProjectMemberError
)


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)


@router.get("/", response_model=List[ProjectResponse])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtém todos os projetos.
    
    Args:
        skip: Número de registros para pular
        limit: Número máximo de registros a retornar
        db: Sessão do banco de dados
    
    Returns:
        List[ProjectResponse]: Lista de projetos
    """
    projects = ProjectController.get_projects(db, skip=skip, limit=limit)
    return projects


@router.get("/user/{user_id}", response_model=List[ProjectResponse])
def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    """
    Obtém os projetos de um usuário.
    
    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados
    
    Returns:
        List[ProjectResponse]: Lista de projetos do usuário
    """
    projects = ProjectController.get_user_projects(db, user_id)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Obtém um projeto pelo ID.
    
    Args:
        project_id: ID do projeto
        db: Sessão do banco de dados
    
    Returns:
        ProjectResponse: Dados do projeto
        
    Raises:
        HTTPException: Se o projeto não for encontrado
    """
    try:
        project = ProjectController.get_project_by_id(db, project_id)
        return project
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Cria um novo projeto.
    
    Args:
        project: Dados do projeto a ser criado
        db: Sessão do banco de dados
    
    Returns:
        ProjectResponse: Projeto criado
        
    Raises:
        HTTPException: Se o usuário dono não existir
    """
    try:
        return ProjectController.create_project(
            db, 
            name=project.name, 
            owner_id=project.owner_id, 
            description=project.description
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int = Path(..., description="ID do projeto"),
    project: ProjectUpdate = None,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Atualiza os dados de um projeto.
    
    Args:
        project_id: ID do projeto
        project: Dados a serem atualizados
        user_id: ID do usuário que está realizando a operação
        db: Sessão do banco de dados
    
    Returns:
        ProjectResponse: Projeto atualizado
        
    Raises:
        HTTPException: Se o projeto não for encontrado ou o usuário não for dono
    """
    if user_id is None:
        raise HTTPException(
            status_code=400,
            detail="É necessário fornecer o ID do usuário para atualizar o projeto",
        )
    
    try:
        updated_project = ProjectController.update_project(
            db, 
            project_id, 
            user_id,
            **project.model_dump(exclude_unset=True)
        )
        return updated_project
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except NotProjectOwnerError as e:
        raise HTTPException(status_code=403, detail=e.message)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Remove um projeto.
    
    Args:
        project_id: ID do projeto
        user_id: ID do usuário que está realizando a operação
        db: Sessão do banco de dados
        
    Raises:
        HTTPException: Se o projeto não for encontrado ou o usuário não for dono
    """
    try:
        ProjectController.delete_project(db, project_id, user_id)
        return None
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except NotProjectOwnerError as e:
        raise HTTPException(status_code=403, detail=e.message)


@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
def add_member(
    project_id: int, 
    member: ProjectMemberCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Adiciona um membro a um projeto.
    
    Args:
        project_id: ID do projeto
        member: Dados do membro a ser adicionado
        user_id: ID do usuário que está realizando a operação
        db: Sessão do banco de dados
    
    Returns:
        ProjectMemberResponse: Membro adicionado
        
    Raises:
        HTTPException: Se o projeto não for encontrado, o usuário não for dono,
                      ou o membro já existir
    """
    try:
        return ProjectController.add_member(
            db, 
            project_id, 
            user_id, 
            member.user_id, 
            role=member.role
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except NotProjectOwnerError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except AlreadyProjectMemberError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.put("/{project_id}/members/{member_id}", response_model=ProjectMemberResponse)
def update_member(
    project_id: int,
    member_id: int,
    member: ProjectMemberUpdate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Atualiza o papel de um membro no projeto.
    
    Args:
        project_id: ID do projeto
        member_id: ID do usuário membro
        member: Dados a serem atualizados
        user_id: ID do usuário que está realizando a operação
        db: Sessão do banco de dados
    
    Returns:
        ProjectMemberResponse: Membro atualizado
        
    Raises:
        HTTPException: Se o projeto não for encontrado, o usuário não for dono,
                      ou o membro não existir
    """
    try:
        # O método remove_member não existe no ProjectController, então precisamos
        # implementá-lo ou usar outra abordagem
        raise NotImplementedError("Método não implementado")
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except NotProjectOwnerError as e:
        raise HTTPException(status_code=403, detail=e.message)


@router.delete("/{project_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: int,
    member_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove um membro de um projeto.
    
    Args:
        project_id: ID do projeto
        member_id: ID do usuário membro
        user_id: ID do usuário que está realizando a operação
        db: Sessão do banco de dados
        
    Raises:
        HTTPException: Se o projeto não for encontrado, o usuário não for dono,
                      ou o membro não existir
    """
    try:
        ProjectController.remove_member(db, project_id, user_id, member_id)
        return None
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except NotProjectOwnerError as e:
        raise HTTPException(status_code=403, detail=e.message) 