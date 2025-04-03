"""
Modelo de associação entre usuários e projetos
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from gestao_projetos.core.database import Base


class ProjectMember(Base):
    """
    Modelo de associação entre usuários e projetos.
    
    Representa a participação de um usuário em um projeto, incluindo seu papel.
    """
    __tablename__ = "project_members"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String, default="membro", nullable=False)
    joined_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relações
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
    
    def __repr__(self):
        return f"<ProjectMember(project_id={self.project_id}, user_id={self.user_id}, role='{self.role}')>" 