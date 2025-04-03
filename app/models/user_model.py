from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, nullable=True)

    owned_projects = relationship("Projects", back_populates="owner", cascade="all, delete-orphan")
    projects_memberships = relationship("ProjectMembers", back_populates="user", cascade="all, delete-orphan")
    user_tasks = relationship("Tasks", back_populates="assigned_user", cascade="all, delete-orphan") 