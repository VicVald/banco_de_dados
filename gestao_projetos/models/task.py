"""
Modelo de tarefa do sistema
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from gestao_projetos.core.database import Base
from gestao_projetos.core.exceptions import InvalidTaskStateError


class Task(Base):
    """
    Modelo de tarefa do sistema.
    
    Representa uma tarefa que pertence a um projeto e pode ser atribuída a um usuário.
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    state = Column(String, default="backlog", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relações
    project = relationship("Project", back_populates="tasks")
    assigned_user = relationship("User", back_populates="assigned_tasks")
    
    # Constraint para garantir que número da tarefa é único dentro do projeto
    __table_args__ = (
        UniqueConstraint('task_number', 'project_id', name='uq_task_number_project'),
    )
    
    # Estados válidos
    VALID_STATES = ["backlog", "em_progresso", "em_revisao", "concluida"]
    
    # Transições válidas de estado
    VALID_TRANSITIONS = {
        "backlog": ["em_progresso"],
        "em_progresso": ["em_revisao", "backlog"],
        "em_revisao": ["em_progresso", "concluida"],
        "concluida": ["em_revisao"]
    }
    
    def change_state(self, new_state):
        """
        Altera o estado da tarefa, validando se a transição é permitida.
        
        Args:
            new_state: Novo estado da tarefa
            
        Returns:
            Task: A própria tarefa com estado atualizado
            
        Raises:
            InvalidTaskStateError: Se a transição de estado não for válida
        """
        if new_state not in self.VALID_STATES:
            raise InvalidTaskStateError(self.state, new_state)
            
        if new_state not in self.VALID_TRANSITIONS.get(self.state, []):
            raise InvalidTaskStateError(self.state, new_state)
            
        self.state = new_state
        return self
        
    def assign_to_user(self, user_id):
        """
        Atribui a tarefa a um usuário.
        
        Args:
            user_id: ID do usuário a quem atribuir a tarefa
            
        Returns:
            Task: A própria tarefa com usuário atualizado
        """
        self.user_id = user_id
        return self
        
    def __repr__(self):
        return f"<Task(id={self.id}, number={self.task_number}, project_id={self.project_id}, state='{self.state}')>" 