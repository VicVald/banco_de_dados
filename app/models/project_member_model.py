from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class ProjectMembers(Base):
    __tablename__ = 'project_users'
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    joined_at = Column(DateTime, default=datetime.now(timezone.utc), index=True)  
    role = Column(String, default="sem funcao", index=True)

    project = relationship("Projects", back_populates="members")
    user = relationship("Users", back_populates="projects_memberships") 