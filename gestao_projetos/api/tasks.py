"""
Rotas da API para tarefas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List

from gestao_projetos.api.schemas import (
    TaskCreate, 
    TaskUpdate, 
    TaskResponse, 
    TaskAssign,
    TaskChangeState,
    ErrorResponse
)
from gestao_projetos.controllers.task_controller import TaskController
from gestao_projetos.core.database import get_db
from gestao_projetos.core.exceptions import (
    ResourceNotFoundException,
    TaskNumberDuplicateError,
    NotProjectOwnerError,
    InvalidTaskStateError
)


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)


@router.get("/project/{project_id}", response_model=List[TaskResponse])
def get_project_tasks(project_id: int, db: Session = Depends(get_db)):
    """
    Obtém todas as tarefas de um projeto.
    
    Args:
        project_id: ID do projeto
        db: Sessão do banco de dados
    
    Returns:
        List[TaskResponse]: Lista de tarefas do projeto
    """
    try:
        tasks = TaskController.get_tasks(db, project_id)
        return tasks
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Obtém uma tarefa pelo ID.
    
    Args:
        task_id: ID da tarefa
        db: Sessão do banco de dados
    
    Returns:
        TaskResponse: Dados da tarefa
        
    Raises:
        HTTPException: Se a tarefa não for encontrada
    """
    try:
        task = TaskController.get_task_by_id(db, task_id)
        return task
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova tarefa.
    
    Args:
        task: Dados da tarefa a ser criada
        db: Sessão do banco de dados
    
    Returns:
        TaskResponse: Tarefa criada
        
    Raises:
        HTTPException: Se o projeto não existir, o usuário não existir,
                      ou o número da tarefa já estiver em uso
    """
    try:
        return TaskController.create_task(
            db, 
            project_id=task.project_id, 
            title=task.title, 
            user_id=task.user_id, 
            description=task.description, 
            state=task.state
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except TaskNumberDuplicateError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except InvalidTaskStateError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int = Path(..., description="ID da tarefa"),
    task: TaskUpdate = None,
    db: Session = Depends(get_db)
):
    """
    Atualiza os dados de uma tarefa.
    
    Args:
        task_id: ID da tarefa
        task: Dados a serem atualizados
        db: Sessão do banco de dados
    
    Returns:
        TaskResponse: Tarefa atualizada
        
    Raises:
        HTTPException: Se a tarefa não for encontrada ou a transição de estado for inválida
    """
    try:
        updated_task = TaskController.update_task(
            db, 
            task_id,
            **task.model_dump(exclude_unset=True)
        )
        return updated_task
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except InvalidTaskStateError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Remove uma tarefa.
    
    Args:
        task_id: ID da tarefa
        user_id: ID do usuário que está realizando a operação
        db: Sessão do banco de dados
        
    Raises:
        HTTPException: Se a tarefa não for encontrada ou o usuário não for dono do projeto
    """
    try:
        TaskController.delete_task(db, task_id, user_id)
        return None
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except NotProjectOwnerError as e:
        raise HTTPException(status_code=403, detail=e.message)


@router.post("/{task_id}/assign", response_model=TaskResponse)
def assign_task(
    task_id: int,
    assignment: TaskAssign,
    db: Session = Depends(get_db)
):
    """
    Atribui uma tarefa a um usuário.
    
    Args:
        task_id: ID da tarefa
        assignment: Dados da atribuição
        db: Sessão do banco de dados
    
    Returns:
        TaskResponse: Tarefa atualizada
        
    Raises:
        HTTPException: Se a tarefa ou o usuário não for encontrado
    """
    try:
        return TaskController.assign_task(db, task_id, assignment.user_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/{task_id}/state", response_model=TaskResponse)
def change_task_state(
    task_id: int,
    state_change: TaskChangeState,
    db: Session = Depends(get_db)
):
    """
    Altera o estado de uma tarefa.
    
    Args:
        task_id: ID da tarefa
        state_change: Dados da mudança de estado
        db: Sessão do banco de dados
    
    Returns:
        TaskResponse: Tarefa atualizada
        
    Raises:
        HTTPException: Se a tarefa não for encontrada ou a transição de estado for inválida
    """
    try:
        return TaskController.change_task_state(db, task_id, state_change.state)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except InvalidTaskStateError as e:
        raise HTTPException(status_code=400, detail=e.message) 