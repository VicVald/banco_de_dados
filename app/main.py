# Importações necessárias para o funcionamento do FastAPI e interação com o banco de dados
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated, Optional
from .models.userModels import *
from .database import engine, SessionLocal
from sqlalchemy.orm import Session, joinedload
from .controllers import userController, projectController, memberController, taskController

# Inicialização do aplicativo FastAPI
app = FastAPI()

# Criação das tabelas no banco de dados com base nos modelos definidos
Base.metadata.create_all(bind=engine)

# __________________
# Modelos Pydantic para validação dos dados recebidos nas requisições
# Garantem que os dados estejam corretos antes de serem processados
# __________________

# Modelo base para usuário
class UserBase(BaseModel):
    name: str
    email: str

# Modelo para criação de usuário
class UserCreate(UserBase):
    pass

# Modelo para atualização parcial de usuário
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

# Modelo de resposta para usuário
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# Modelo base para projeto
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: int

# Modelo para criação de projeto
class ProjectCreate(ProjectBase):
    pass

# Modelo para atualização parcial de projeto
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Modelo para adicionar membro ao projeto
class ProjectMemberCreate(BaseModel):
    user_id: int
    role: str = "sem funcao"

# Modelo para atualização parcial de membro do projeto
class ProjectMemberUpdate(BaseModel):
    role: Optional[str] = None

# Modelo de resposta para membro do projeto
class ProjectMemberResponse(BaseModel):
    user: UserResponse
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True

# Modelo de resposta para projeto
class ProjectResponse(ProjectBase):
    id: int
    owner: UserResponse
    members: List[ProjectMemberResponse]

    class Config:
        from_attributes = True

# Modelo base para tarefa
class TaskBase(BaseModel):
    name: str
    description: str
    state: str
    user_id: int
    project_id: int

# Modelo para criação de tarefa
class TaskCreate(TaskBase):
    pass

# Modelo para atualização parcial de tarefa
class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    user_id: Optional[int] = None

# Modelo de resposta para tarefa
class TaskResponse(TaskBase):
    id: int
    user: UserResponse
    project: ProjectResponse
    task_number: int

    class Config:
        from_attributes = True

# Função para obter uma sessão do banco de dados
# Utilizada para realizar operações no banco

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# __________________
# Rotas para operações CRUD relacionadas aos usuários
# __________________

# Obter todos os usuários
@app.get("/users/", response_model=List[UserResponse])
async def read_users(db: db_dependency):
    return userController.get_all_users(db)

# Criar um novo usuário
@app.post("/users/", response_model=UserResponse)
async def create_users(user: UserCreate, db: db_dependency):
    return userController.create_new_user(user=user, db=db)

# Atualizar um usuário existente
@app.put("/users/{user_id}", response_model=UserResponse)
async def update_users(user_id: int, user_data: UserUpdate, db: db_dependency):
    return userController.update_existing_user(user_id=user_id, user_data=user_data, db=db)

# Deletar um usuário existente
@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int, db: db_dependency):
    return userController.delete_existing_user(user_id=user_id, db=db)

# __________________
# Rotas para operações CRUD relacionadas aos projetos
# __________________

# Obter detalhes de um projeto específico
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
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return db_project

# Criar um novo projeto
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

# Atualizar um projeto existente
@app.put("/projects/{project_id}")
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

# Deletar um projeto existente
@app.delete("/projects/{project_id}")
async def delete_project(project_id: int, db: db_dependency):
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Projeto Apagado com Sucesso"}

# __________________
# Rotas para operações CRUD relacionadas aos membros dos projetos
# __________________

# Adicionar membro ao projeto
@app.post("/projects/{project_id}/members/", response_model=dict)
async def add_member(project_id: int, member: ProjectMemberCreate, db: db_dependency):
    return memberController.add_member_to_project(project_id=project_id, member=member, db=db)

# Atualizar um membro do projeto
@app.put("/projects/{project_id}/members/{member_id}", response_model=dict)
async def update_member(project_id: int, member_id: int, member: ProjectMemberUpdate, db: db_dependency):
    return memberController.update_project_member(project_id=project_id, member_id=member_id, member=member, db=db)

# Deletar um membro do projeto
@app.delete("/projects/{project_id}/members/{member_id}", response_model=dict)
async def delete_member(project_id: int, member_id: int, db: db_dependency):
    db_member = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    
    db.delete(db_member)
    db.commit()
    return {"message": "Membro Apagado com Sucesso"}

# __________________
# Rotas para operações CRUD relacionadas às tarefas dos projetos
# __________________

# Obter todas as tarefas de um projeto
@app.get("/projects/{project_id}/tasks/")
async def read_tasks(project_id: int, db: db_dependency):
    return taskController.get_tasks_by_project(project_id, db)

# Criar uma nova tarefa em um projeto
@app.post("/projects/{project_id}/tasks/")
async def create_task(project_id: int, task: TaskBase, db: db_dependency):
    return taskController.create_task_for_project(project_id, task, db)

# Atualizar uma tarefa de um membro em um projeto
@app.put("/projects/{project_id}/members/{member_id}/tasks/{task_number}")
async def update_task(project_id: int, member_id: int, task_number: int, task: TaskUpdate, db: db_dependency):
    return taskController.update_task(project_id, member_id, task_number, task, db)

# Deletar uma tarefa de um membro em um projeto
@app.delete("/projects/{project_id}/members/{member_id}/tasks/{task_number}")
async def delete_task(project_id: int, member_id: int, task_number: int, db: db_dependency):
    return taskController.delete_task(project_id, member_id, task_number, db)

# Obter todas as tarefas de um membro específico em um projeto
@app.get("/projects/{project_id}/members/{member_id}/tasks/")
async def read_tasks_per_member(project_id: int, member_id: int, db: db_dependency):
    result = db.query(Tasks).filter(Tasks.project_id == project_id, Tasks.user_id == member_id).all()

    if not result:
        raise HTTPException(status_code=404, detail="No tasks for this member in this project")
    
    return result
