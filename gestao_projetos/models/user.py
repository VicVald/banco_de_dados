"""
Modelo de usuário do sistema
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from gestao_projetos.core.database import Base


class User(Base):
    """
    Modelo de usuário do sistema.
    
    Representa um usuário que pode possuir projetos e ser atribuído a tarefas.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relações
    owned_projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    assigned_tasks = relationship("Task", back_populates="assigned_user")
    
    def is_project_owner(self, project_id):
        """
        Verifica se o usuário é dono de um projeto específico.
        
        Args:
            project_id: ID do projeto a verificar
            
        Returns:
            bool: True se o usuário for dono do projeto, False caso contrário
        """
        return any(project.id == project_id for project in self.owned_projects)
    
    def is_project_member(self, project_id):
        """
        Verifica se o usuário é membro (incluindo dono) de um projeto específico.
        
        Args:
            project_id: ID do projeto a verificar
            
        Returns:
            bool: True se o usuário for membro do projeto, False caso contrário
        """
        # Verifica se é dono
        if self.is_project_owner(project_id):
            return True
        
        # Verifica se é membro
        return any(membership.project_id == project_id for membership in self.project_memberships)
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>" 