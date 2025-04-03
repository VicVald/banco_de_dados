"""
Controller de projetos
"""
from sqlalchemy.orm import Session, joinedload
from gestao_projetos.models.project import Project
from gestao_projetos.models.member import ProjectMember
from gestao_projetos.models.user import User
from gestao_projetos.models.task import Task
from gestao_projetos.core.exceptions import (
    ResourceNotFoundException,
    NotProjectOwnerError,
    AlreadyProjectMemberError
)
from gestao_projetos.controllers.user_controller import UserController


class ProjectController:
    """
    Controller para gerenciamento de projetos.
    
    Implementa a lógica de negócio relacionada a projetos e membros.
    """
    
    @staticmethod
    def get_projects(db: Session, skip: int = 0, limit: int = 100):
        """
        Obtém a lista de projetos.
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular (para paginação)
            limit: Número máximo de registros a retornar
            
        Returns:
            list: Lista de projetos
        """
        return db.query(Project).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_projects(db: Session, user_id: int):
        """
        Obtém a lista de projetos que um usuário possui ou participa.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            
        Returns:
            list: Lista de projetos
        """
        # Projetos que o usuário é dono
        owned_projects = db.query(Project).filter(Project.owner_id == user_id).all()
        
        # Projetos que o usuário é membro
        member_projects = (
            db.query(Project)
            .join(ProjectMember)
            .filter(ProjectMember.user_id == user_id)
            .all()
        )
        
        # Combinar os resultados (eliminando duplicatas)
        all_projects = {p.id: p for p in owned_projects}
        for project in member_projects:
            if project.id not in all_projects:
                all_projects[project.id] = project
                
        return list(all_projects.values())
    
    @staticmethod
    def get_project_by_id(db: Session, project_id: int):
        """
        Obtém um projeto pelo ID.
        
        Args:
            db: Sessão do banco de dados
            project_id: ID do projeto
            
        Returns:
            Project: Projeto encontrado
            
        Raises:
            ResourceNotFoundException: Se o projeto não for encontrado
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise ResourceNotFoundException("Projeto", project_id)
        return project
    
    @staticmethod
    def create_project(db: Session, name: str, owner_id: int, description: str = None):
        """
        Cria um novo projeto.
        
        Args:
            db: Sessão do banco de dados
            name: Nome do projeto
            owner_id: ID do usuário dono do projeto
            description: Descrição do projeto (opcional)
            
        Returns:
            Project: Projeto criado
            
        Raises:
            ResourceNotFoundException: Se o usuário não for encontrado
        """
        # Verifica se o usuário existe
        UserController.get_user_by_id(db, owner_id)
        
        # Cria o projeto
        project = Project(name=name, owner_id=owner_id, description=description)
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def update_project(db: Session, project_id: int, user_id: int, **kwargs):
        """
        Atualiza os dados de um projeto.
        
        Args:
            db: Sessão do banco de dados
            project_id: ID do projeto
            user_id: ID do usuário que está realizando a operação
            **kwargs: Campos a serem atualizados
            
        Returns:
            Project: Projeto atualizado
            
        Raises:
            ResourceNotFoundException: Se o projeto não for encontrado
            NotProjectOwnerError: Se o usuário não for dono do projeto
        """
        project = ProjectController.get_project_by_id(db, project_id)
        
        # Verifica se o usuário é dono do projeto
        if project.owner_id != user_id:
            raise NotProjectOwnerError(user_id, project_id)
        
        # Atualiza apenas os campos fornecidos
        for key, value in kwargs.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)
        
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def delete_project(db: Session, project_id: int, user_id: int):
        """
        Remove um projeto.
        
        Args:
            db: Sessão do banco de dados
            project_id: ID do projeto
            user_id: ID do usuário que está realizando a operação
            
        Returns:
            bool: True se o projeto foi removido
            
        Raises:
            ResourceNotFoundException: Se o projeto não for encontrado
            NotProjectOwnerError: Se o usuário não for dono do projeto
        """
        project = ProjectController.get_project_by_id(db, project_id)
        
        # Verifica se o usuário é dono do projeto
        if project.owner_id != user_id:
            raise NotProjectOwnerError(user_id, project_id)
        
        db.delete(project)
        db.commit()
        return True
    
    @staticmethod
    def add_member(db: Session, project_id: int, user_id: int, member_user_id: int, role: str = "membro"):
        """
        Adiciona um membro ao projeto.
        
        Args:
            db: Sessão do banco de dados
            project_id: ID do projeto
            user_id: ID do usuário que está realizando a operação
            member_user_id: ID do usuário a ser adicionado como membro
            role: Papel do usuário no projeto
            
        Returns:
            ProjectMember: Membro adicionado
            
        Raises:
            ResourceNotFoundException: Se o projeto ou usuário não for encontrado
            NotProjectOwnerError: Se o usuário não for dono do projeto
            AlreadyProjectMemberError: Se o usuário já for membro do projeto
        """
        project = ProjectController.get_project_by_id(db, project_id)
        
        # Verifica se o usuário é dono do projeto
        if project.owner_id != user_id:
            raise NotProjectOwnerError(user_id, project_id)
        
        # Verifica se o usuário a ser adicionado existe
        UserController.get_user_by_id(db, member_user_id)
        
        # Verifica se o usuário já é membro
        existing_member = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == member_user_id
            )
            .first()
        )
        
        if existing_member:
            raise AlreadyProjectMemberError(member_user_id, project_id)
        
        # Adiciona o membro
        member = ProjectMember(
            project_id=project_id,
            user_id=member_user_id,
            role=role
        )
        
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    
    @staticmethod
    def remove_member(db: Session, project_id: int, user_id: int, member_user_id: int):
        """
        Remove um membro de um projeto.
        
        Args:
            db: Sessão do banco de dados
            project_id: ID do projeto
            user_id: ID do usuário que está realizando a operação
            member_user_id: ID do usuário a ser removido
            
        Returns:
            bool: True se o membro foi removido
            
        Raises:
            ResourceNotFoundException: Se o projeto ou membro não for encontrado
            NotProjectOwnerError: Se o usuário não for dono do projeto
        """
        project = ProjectController.get_project_by_id(db, project_id)
        
        # Verifica se o usuário é dono do projeto
        if project.owner_id != user_id:
            raise NotProjectOwnerError(user_id, project_id)
        
        # Verifica se o membro existe
        member = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == member_user_id
            )
            .first()
        )
        
        if not member:
            raise ResourceNotFoundException("Membro", f"{project_id}:{member_user_id}")
        
        db.delete(member)
        db.commit()
        return True
    
    @staticmethod
    def list_tasks_with_members(db: Session, project_id: int):
        """
        Lista todas as tarefas de um projeto com informações dos membros atribuídos.
        
        Args:
            db: Sessão do banco de dados
            project_id: ID do projeto
            
        Returns:
            list: Lista de tarefas com informações dos membros
            
        Raises:
            ResourceNotFoundException: Se o projeto não for encontrado
        """
        # Verifica se o projeto existe
        ProjectController.get_project_by_id(db, project_id)
        
        # Busca as tarefas com join nas tabelas de usuários
        tasks = (
            db.query(Task)
            .options(joinedload(Task.assigned_user))
            .filter(Task.project_id == project_id)
            .all()
        )
        
        return tasks 