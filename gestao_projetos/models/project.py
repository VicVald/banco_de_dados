"""
Modelo de projeto do sistema
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from gestao_projetos.core.database import Base


class Project(Base):
    """
    Modelo de projeto do sistema.
    
    Representa um projeto que possui tarefas e membros.
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relações
    owner = relationship("User", back_populates="owned_projects")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    
    def add_member(self, user_id, role="membro"):
        """
        Adiciona um membro ao projeto.
        
        Args:
            user_id: ID do usuário a ser adicionado
            role: Papel do usuário no projeto (padrão: "membro")
            
        Returns:
            ProjectMember: Objeto de associação entre projeto e usuário
        """
        from gestao_projetos.models.member import ProjectMember
        member = ProjectMember(project_id=self.id, user_id=user_id, role=role)
        return member
    
    def get_next_task_number(self):
        """
        Obtém o próximo número de tarefa disponível para o projeto.
        
        Returns:
            int: Próximo número de tarefa
        """
        if not self.tasks:
            return 1
        
        # Encontra o maior número de tarefa e adiciona 1
        return max(task.task_number for task in self.tasks) + 1
    
    def is_user_member(self, user_id):
        """
        Verifica se um usuário é membro (ou dono) do projeto.
        
        Args:
            user_id: ID do usuário a verificar
            
        Returns:
            bool: True se o usuário for membro ou dono do projeto, False caso contrário
        """
        # Verifica se é dono
        if self.owner_id == user_id:
            return True
        
        # Verifica se é membro
        return any(member.user_id == user_id for member in self.members)
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', owner_id={self.owner_id})>" 