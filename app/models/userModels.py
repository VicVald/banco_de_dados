# __________________
# Modelos SQLAlchemy que representam as tabelas do banco de dados
# __________________

from sqlalchemy import UniqueConstraint, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base, engine

# Modelo que representa a tabela de usuários
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, nullable=True)

    # Relacionamentos com outras tabelas
    owned_projects = relationship("Projects", back_populates="owner", cascade="all, delete-orphan")
    projects_memberships = relationship("ProjectMembers", back_populates="user", cascade="all, delete-orphan")
    user_tasks = relationship("Tasks", back_populates="assigned_user", cascade="all, delete-orphan")

# Modelo que representa a tabela de projetos
class Projects(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))

    # Relacionamentos com outras tabelas
    owner = relationship("Users", back_populates="owned_projects")
    members = relationship("ProjectMembers", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Tasks", back_populates="project", cascade="all, delete-orphan")

# Modelo que representa a tabela de membros dos projetos
class ProjectMembers(Base):
    __tablename__ = 'project_users'
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    joined_at = Column(DateTime, default=datetime.now(timezone.utc), index=True)
    role = Column(String, default="sem funcao", index=True)

    # Relacionamentos com outras tabelas
    project = relationship("Projects", back_populates="members")
    user = relationship("Users", back_populates="projects_memberships")

# Modelo que representa a tabela de tarefas
class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    task_number = Column(Integer, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    state = Column(String, index=True)

    # Restrição única para garantir que cada tarefa tenha um número único dentro do mesmo projeto
    __table_args__ = (
        UniqueConstraint('project_id', 'task_number', name='uq_project_task_number'),
    )

    # Relacionamentos com outras tabelas
    project = relationship("Projects", back_populates="tasks")
    assigned_user = relationship("Users", back_populates="user_tasks")

