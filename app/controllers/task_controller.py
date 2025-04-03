from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.task_model import Tasks
from app.models.project_model import Projects
from app.schemas.task_schema import TaskCreate, TaskUpdate

class TaskController:
    @staticmethod
    def get_project_tasks(db: Session, project_id: int):
        # Verifica se o projeto existe
        db_project = db.query(Projects).filter(Projects.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        # Busca todas as tarefas do projeto
        tasks = db.query(Tasks).filter(Tasks.project_id == project_id).all()
        return tasks
    
    @staticmethod
    def get_member_tasks(db: Session, project_id: int, member_id: int):
        # Verifica se o projeto existe
        db_project = db.query(Projects).filter(Projects.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        # Busca todas as tarefas do membro no projeto
        tasks = db.query(Tasks).filter(
            Tasks.project_id == project_id,
            Tasks.user_id == member_id
        ).all()
        
        return tasks
    
    @staticmethod
    def create_task(db: Session, project_id: int, task: TaskCreate):
        # Verifica se o projeto existe
        db_project = db.query(Projects).filter(Projects.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        # Determina o número da próxima tarefa no projeto
        max_task_number = db.query(Tasks).filter(Tasks.project_id == project_id).count() + 1
        
        # Cria a nova tarefa
        db_task = Tasks(
            name=task.name,
            description=task.description,
            state=task.state,
            user_id=task.user_id,
            project_id=project_id,
            task_number=max_task_number
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        return db_task
    
    @staticmethod
    def update_task(db: Session, project_id: int, member_id: int, task_number: int, task_data: TaskUpdate):
        # Busca a tarefa específica
        db_task = db.query(Tasks).filter(
            Tasks.project_id == project_id,
            Tasks.user_id == member_id,
            Tasks.task_number == task_number
        ).first()
        
        if not db_task:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        
        # Atualiza os campos da tarefa
        for key, value in task_data.model_dump(exclude_unset=True).items():
            if value == 'string':
                continue
            setattr(db_task, key, value)
        
        db.commit()
        db.refresh(db_task)
        
        return db_task
    
    @staticmethod
    def delete_task(db: Session, project_id: int, member_id: int, task_number: int):
        # Busca a tarefa específica
        db_task = db.query(Tasks).filter(
            Tasks.project_id == project_id,
            Tasks.user_id == member_id,
            Tasks.task_number == task_number
        ).first()
        
        if not db_task:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        
        db.delete(db_task)
        db.commit()
        
        return {"message": "Tarefa removida com sucesso"} 