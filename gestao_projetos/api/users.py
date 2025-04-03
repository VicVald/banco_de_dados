"""
Rotas da API para usuários
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from gestao_projetos.api.schemas import UserCreate, UserUpdate, UserResponse, ErrorResponse
from gestao_projetos.controllers.user_controller import UserController
from gestao_projetos.core.database import get_db
from gestao_projetos.core.exceptions import ResourceNotFoundException


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"model": ErrorResponse}},
)


@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtém todos os usuários.
    
    Args:
        skip: Número de registros para pular
        limit: Número máximo de registros a retornar
        db: Sessão do banco de dados
    
    Returns:
        List[UserResponse]: Lista de usuários
    """
    users = UserController.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Obtém um usuário pelo ID.
    
    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados
    
    Returns:
        UserResponse: Dados do usuário
        
    Raises:
        HTTPException: Se o usuário não for encontrado
    """
    try:
        user = UserController.get_user_by_id(db, user_id)
        return user
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário.
    
    Args:
        user: Dados do usuário a ser criado
        db: Sessão do banco de dados
    
    Returns:
        UserResponse: Usuário criado
        
    Raises:
        HTTPException: Se já existir um usuário com o mesmo email
    """
    # Verifica se já existe um usuário com o mesmo email
    db_user = UserController.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe um usuário com o email '{user.email}'",
        )
    
    # Cria o usuário
    return UserController.create_user(db, name=user.name, email=user.email)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """
    Atualiza os dados de um usuário.
    
    Args:
        user_id: ID do usuário
        user: Dados a serem atualizados
        db: Sessão do banco de dados
    
    Returns:
        UserResponse: Usuário atualizado
        
    Raises:
        HTTPException: Se o usuário não for encontrado
    """
    try:
        # Verificar se o email já está sendo usado por outro usuário
        if user.email:
            existing_user = UserController.get_user_by_email(db, user.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Email '{user.email}' já está sendo usado por outro usuário",
                )
        
        # Atualiza o usuário
        updated_user = UserController.update_user(
            db, 
            user_id, 
            **user.model_dump(exclude_unset=True)
        )
        return updated_user
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Remove um usuário.
    
    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados
        
    Raises:
        HTTPException: Se o usuário não for encontrado
    """
    try:
        UserController.delete_user(db, user_id)
        return None
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message) 