from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated, Optional
from .models import *
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

app = FastAPI()
Base.metadata.create_all(bind=engine)

#Pydantic Models for represent the database
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
    


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: int

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    #add to change owner_id, need to change the put route to change member to owner and owner to be a member


class ProjectMemberCreate(BaseModel):
    user_id: int
    role: str = "sem funcao"

class ProjectMemberUpdate(BaseModel):
    role: Optional[str] = None

class ProjectMemberResponse(BaseModel):
    user: UserResponse
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True

class ProjectResponse(ProjectBase):
    id: int
    owner: UserResponse
    members: List[ProjectMemberResponse]

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    name: str
    description: str
    state: str

    user_id: int
    project_id: int

class TaskCreate(TaskBase):
    pass 

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None

    user_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    user: UserResponse
    project: ProjectResponse
    task_number: int

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/users/")
async def read_users(db: db_dependency):
    result = db.query(Users).all()
    if not result:
        raise HTTPException(status_code=404, detail="Users not found!")
    return result

@app.post("/users/")
async def create_users(user: UserBase, db: db_dependency):
    db_user = Users(
        name=user.name,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.put("/users/{user_id}")
async def update_users(user_id: int, user_data: UserUpdate, db: db_dependency):
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    for key, value in user_data.model_dump(exclude_unset=True).items():
        if value == 'string':
            continue
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: db_dependency):
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(db_user)
    db.commit()
    return {"message": "Usuario Apagado com Sucesso"}



@app.get("/projects/{project_id}")
async def read_projects(project_id: int, db: db_dependency):
    db_project = (
        db.query(Projects)
        .options(
            joinedload(Projects.owner),
            joinedload(Projects.members).joinedload(ProjectMembers.user)
        )
        .filter(Projects.id == project_id)
        .first()
    )
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Projects not found!")
    return db_project


@app.post("/projects/")
async def create_projects(project: ProjectBase, db: db_dependency):
    db_project = Projects(
        name=project.name,
        description=project.description,
        owner_id=project.owner_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project

@app.put("/projects{project_id}")
async def update_project(project_id: int, project_data: ProjectUpdate, db: db_dependency):
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    for key, value in project_data.model_dump(exclude_unset=True).items():
        if value == 'string':
            continue
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/projects{project_id}")
async def delete_project(project_id: int, db: db_dependency):
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Projeto Apagado com Sucesso"}

@app.post("/projects/{project_id}/members/", response_model=dict)
async def add_member(project_id: int, member: ProjectMemberCreate, db: db_dependency):
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    db_user = db.query(Users).filter(Users.id == member.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db_member = ProjectMembers(
        project_id=project_id,
        user_id=member.user_id,
        role=member.role
    )
    
    db.add(db_member)
    db.commit()
    return {"message": f"Membro {member.user_id} adicionado com sucesso no projeto {project_id}"}

@app.put("/projects/{project_id}/members/{member_id}")
async def update_member(project_id: int, member_id: int, member: ProjectMemberUpdate, db: db_dependency):
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    db_user = db.query(Users).filter(Users.id == member_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db_member = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    
    for key, value in member.model_dump(exclude_unset=True).items():
        if value == 'string':
            continue
        setattr(db_member, key, value)
    
    db.commit()
    db.refresh(db_member)
    return db_member

@app.delete("/projects/{project_id}/members/{member_id}")
async def delete_member(project_id: int, member_id: int, db: db_dependency):
    db_member = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    
    db.delete(db_member)
    db.commit()
    return {"message": "Membro Apagado com Sucesso"}

@app.get("/projects/{project_id}/tasks/")
async def read_tasks(project_id: int, db: db_dependency):
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    result = db.query(Tasks).filter(Tasks.project_id == project_id).all()
    if not result:
        raise HTTPException(status_code=404, detail="Projeto sem tasks")
    return result

@app.post("/projects/{project_id}/tasks/")
async def create_task(project_id: int, task: TaskBase, db: db_dependency):

    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    
    last_task = db.query(Tasks).filter(Tasks.project_id == project_id)\
                    .order_by(Tasks.task_number.desc()).first()
    
    new_task_number = 1
    if last_task:
        new_task_number = last_task.task_number + 1

    db_task = Tasks(
        task_number=new_task_number,
        name=task.name,
        description=task.description,
        state=task.state,
        user_id=task.user_id,
        project_id=project_id
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

#
#
# AS TASKS PRECISAM TER ID DE ACORDO COM O PROJETO PODE EXISTIR VARIOS ID's 1 por'em apenas um por projeto
# PRECISAM SER ADICIONADAS MAIS VALIDAÇ~OES
# PRECISA-SE manter consistencia no c'odigo
#
#

@app.get("/projects/{project_id}/members/{member_id}/tasks/")
async def read_tasks_per_member(project_id: int, member_id: int, db: db_dependency):
    result = db.query(Tasks).filter(Tasks.project_id == project_id, Tasks.user_id == member_id).all()

    if not result:
        raise HTTPException(status_code=404, detail="No tasks for this member in this project")
    
    return result

@app.put("/projects/{project_id}/members/{member_id}/tasks/{task_number}")
async def update_task(project_id: int, member_id: int, task_number: int, task: TaskUpdate, db: db_dependency):
    db_task = db.query(Tasks).filter(Tasks.project_id == project_id, Tasks.user_id == member_id, Tasks.task_number == task_number).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task não encontrada")

    for key, value in task.model_dump(exclude_unset=True).items():
        if value == 'string':
            continue
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/projects/{project_id}/members/{member_id}/tasks/{task_number}")
async def delete_task(project_id: int, member_id: int, task_number: int, db: db_dependency):
    db_task = db.query(Tasks).filter(Tasks.project_id == project_id, Tasks.user_id == member_id, Tasks.task_number == task_number).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    
    db.delete(db_task)
    db.commit()
    return {'message': f"Task {task_number} no projeto {project_id} deletada com sucesso!"}






























# #Auth Route
# @app.post("/auth/register/")
# async def user_register(db: db_dependency):
#     ...
# @app.post("/auth/login/")
# async def user_login(db: db_dependency):
#     ...

# #Users Route
# @app.get("/users/me/")
# @app.put("/users/me/")
# @app.delete("/users/me/")

# #Projects Route
# @app.get("/projects/")
# @app.post("/projects/")

# @app.get("/projects/{project_id}/")
# @app.put("/projects/{project_id}/")
# @app.delete("/projects/{project_id}/")

# #Tasks

# @app.get("/projects/{project_id}/tasks/")
# @app.post("/projects/{project_id}/tasks/")

# @app.get("/projects/{project_id}/tasks/{task_id}/")
# @app.put("/projects/{project_id}/tasks/{task_id}/")
# @app.delete("/projects/{project_id}/tasks/{task_id}/")
