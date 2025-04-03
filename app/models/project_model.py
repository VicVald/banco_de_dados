from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Projects(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    
    # Relacionamentos
    owner = relationship("Users", back_populates="owned_projects")
    members = relationship("ProjectMembers", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Tasks", back_populates="project", cascade="all, delete-orphan") 