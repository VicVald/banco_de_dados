# __________________
# Controlador responsável pelas operações CRUD relacionadas às tarefas dos projetos
# __________________

from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.userModels import Tasks, Projects
from ..main import TaskBase, TaskUpdate

# Obter todas as tarefas associadas a um projeto específico
def get_tasks_by_project(project_id: int, db: Session):
    tasks = db.query(Tasks).filter(Tasks.project_id == project_id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Projeto sem tarefas")
    return tasks

# Criar uma nova tarefa em um projeto específico
def create_task_for_project(project_id: int, task: TaskBase, db: Session):
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    last_task = db.query(Tasks).filter(Tasks.project_id == project_id).order_by(Tasks.task_number.desc()).first()
    new_task_number = 1 if not last_task else last_task.task_number + 1

    db_task = Tasks(task_number=new_task_number, name=task.name, description=task.description, state=task.state, user_id=task.user_id, project_id=project_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Atualizar informações de uma tarefa existente
def update_task(project_id: int, member_id: int, task_number: int, task: TaskUpdate, db: Session):
    db_task = db.query(Tasks).filter(Tasks.project_id == project_id, Tasks.user_id == member_id, Tasks.task_number == task_number).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task

# Deletar uma tarefa existente de um projeto
def delete_task(project_id: int, member_id: int, task_number: int, db: Session):
    db_task = db.query(Tasks).filter(Tasks.project_id == project_id, Tasks.user_id == member_id, Tasks.task_number == task_number).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    db.delete(db_task)
    db.commit()
    return {'message': f"Tarefa {task_number} no projeto {project_id} deletada com sucesso!"}