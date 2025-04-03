from sqlalchemy import UniqueConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    task_number = Column(Integer, nullable=False)

    project_id = Column(Integer, ForeignKey('projects.id'), index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    state = Column(String, index=True)

    __table_args__ = (
        UniqueConstraint('project_id', 'task_number', name='uq_project_task_number'),
    )

    project = relationship("Projects", back_populates="tasks")
    assigned_user = relationship("Users", back_populates="user_tasks") 