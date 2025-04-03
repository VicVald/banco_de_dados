"""
Controller de tarefas
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from gestao_projetos.models.task import Task
from gestao_projetos.models.project import Project
from gestao_projetos.core.exceptions import (
    ResourceNotFoundException,
    TaskNumberDuplicateError,
    NotProjectOwnerError,
    InvalidTaskStateError
)
from gestao_projetos.controllers.project_controller import ProjectController
from gestao_projetos.controllers.user_controller import UserController


class TaskController:
    """
    Controller para gerenciamento de tarefas.
    
    Implementa a lógica de negócio relacionada a tarefas.
    """
    
    @staticmethod
    def get_tasks(db: Session, project_id: int):
        """
        Obtém a lista de tarefas de um projeto.
        
        Args:
            db: Sessão do banco de dados
            project_id: ID do projeto
            
        Returns:
            list: Lista de tarefas
            
        Raises:
            ResourceNotFoundException: Se o projeto não for encontrado
        """
        # Verifica se o projeto existe
        ProjectController.get_project_by_id(db, project_id)
        
        return db.query(Task).filter(Task.project_id == project_id).all()
    
    @staticmethod
    def get_task_by_id(db: Session, task_id: int):
        """
        Obtém uma tarefa pelo ID.
        
        Args:
            db: Sessão do banco de dados
            task_id: ID da tarefa
            
        Returns:
            Task: Tarefa encontrada
            
        Raises:
            ResourceNotFoundException: Se a tarefa não for encontrada
        """
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            raise ResourceNotFoundException("Tarefa", task_id)
        return task
    
    @staticmethod
    def get_task_by_number(db: Session, project_id: int, task_number: int):
        """
        Obtém uma tarefa pelo número dentro de um projeto.
        
        Args:
            db: Sessão do banco de dados
            project_id: ID do projeto
            task_number: Número da tarefa
            
        Returns:
            Task: Tarefa encontrada ou None se não encontrada
        """
        return (
            db.query(Task)
            .filter(
                Task.project_id == project_id,
                Task.task_number == task_number
            )
            .first()
        )
    
    @staticmethod
    def create_task(db: Session, project_id: int, title: str, user_id: int = None, description: str = None, state: str = "backlog"):
        """
        Cria uma nova tarefa.
        
        Args:
            db: Sessão do banco de dados
            project_id: ID do projeto
            title: Título da tarefa
            user_id: ID do usuário atribuído à tarefa (opcional)
            description: Descrição da tarefa (opcional)
            state: Estado inicial da tarefa (padrão: "backlog")
            
        Returns:
            Task: Tarefa criada
            
        Raises:
            ResourceNotFoundException: Se o projeto ou usuário não for encontrado
            TaskNumberDuplicateError: Se houver conflito no número da tarefa
            InvalidTaskStateError: Se o estado fornecido for inválido
        """
        # Verifica se o projeto existe
        project = ProjectController.get_project_by_id(db, project_id)
        
        # Verifica se o usuário existe (se fornecido)
        if user_id is not None:
            UserController.get_user_by_id(db, user_id)
        
        # Verifica se o estado é válido
        if state not in Task.VALID_STATES:
            raise InvalidTaskStateError("novo", state)
        
        # Determina o próximo número de tarefa
        next_task_number = project.get_next_task_number()
        
        # Cria a tarefa
        task = Task(
            project_id=project_id,
            task_number=next_task_number,
            title=title,
            description=description,
            state=state,
            user_id=user_id
        )
        
        try:
            db.add(task)
            db.commit()
            db.refresh(task)
            return task
        except IntegrityError:
            db.rollback()
            raise TaskNumberDuplicateError(project_id, next_task_number)
    
    @staticmethod
    def update_task(db: Session, task_id: int, **kwargs):
        """
        Atualiza os dados de uma tarefa.
        
        Args:
            db: Sessão do banco de dados
            task_id: ID da tarefa
            **kwargs: Campos a serem atualizados
            
        Returns:
            Task: Tarefa atualizada
            
        Raises:
            ResourceNotFoundException: Se a tarefa não for encontrada
            InvalidTaskStateError: Se o estado fornecido for inválido
        """
        task = TaskController.get_task_by_id(db, task_id)
        
        # Tratamento especial para mudança de estado
        if 'state' in kwargs and kwargs['state'] is not None:
            new_state = kwargs['state']
            # Verificar se a transição de estado é válida
            try:
                task.change_state(new_state)
            except InvalidTaskStateError as e:
                raise e
            # Remover o estado dos kwargs para não atualizar novamente
            del kwargs['state']
        
        # Tratamento especial para atribuição de usuário
        if 'user_id' in kwargs and kwargs['user_id'] is not None:
            user_id = kwargs['user_id']
            # Verificar se o usuário existe
            if user_id is not None:
                UserController.get_user_by_id(db, user_id)
            # Remover o user_id dos kwargs para não atualizar novamente
            del kwargs['user_id']
            task.assign_to_user(user_id)
        
        # Atualiza os demais campos fornecidos
        for key, value in kwargs.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def delete_task(db: Session, task_id: int, user_id: int):
        """
        Remove uma tarefa.
        
        Args:
            db: Sessão do banco de dados
            task_id: ID da tarefa
            user_id: ID do usuário que está realizando a operação
            
        Returns:
            bool: True se a tarefa foi removida
            
        Raises:
            ResourceNotFoundException: Se a tarefa não for encontrada
            NotProjectOwnerError: Se o usuário não for dono do projeto
        """
        task = TaskController.get_task_by_id(db, task_id)
        
        # Obtém o projeto
        project = ProjectController.get_project_by_id(db, task.project_id)
        
        # Verifica se o usuário é dono do projeto
        if project.owner_id != user_id:
            raise NotProjectOwnerError(user_id, project.id)
        
        db.delete(task)
        db.commit()
        return True
    
    @staticmethod
    def assign_task(db: Session, task_id: int, user_id: int):
        """
        Atribui uma tarefa a um usuário.
        
        Args:
            db: Sessão do banco de dados
            task_id: ID da tarefa
            user_id: ID do usuário a quem atribuir a tarefa
            
        Returns:
            Task: Tarefa atualizada
            
        Raises:
            ResourceNotFoundException: Se a tarefa ou usuário não for encontrado
        """
        task = TaskController.get_task_by_id(db, task_id)
        
        # Verifica se o usuário existe
        if user_id is not None:
            UserController.get_user_by_id(db, user_id)
        
        task.user_id = user_id
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def change_task_state(db: Session, task_id: int, new_state: str):
        """
        Altera o estado de uma tarefa.
        
        Args:
            db: Sessão do banco de dados
            task_id: ID da tarefa
            new_state: Novo estado da tarefa
            
        Returns:
            Task: Tarefa atualizada
            
        Raises:
            ResourceNotFoundException: Se a tarefa não for encontrada
            InvalidTaskStateError: Se o estado fornecido for inválido ou a transição não for permitida
        """
        task = TaskController.get_task_by_id(db, task_id)
        
        try:
            task.change_state(new_state)
            db.commit()
            db.refresh(task)
            return task
        except InvalidTaskStateError as e:
            db.rollback()
            raise e 