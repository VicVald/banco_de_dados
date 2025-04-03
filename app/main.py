from fastapi import FastAPI
from app.routes import user_routes, project_routes, task_routes
from app.models.user_model import Users
from app.models.project_model import Projects
from app.models.project_member_model import ProjectMembers
from app.models.task_model import Tasks
from app.database import Base, engine

app = FastAPI(
    title="API de Gerenciamento de Projetos",
    description="API para gerenciamento de projetos, usuários e tarefas",
    version="1.0.0"
)

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inclui as rotas
app.include_router(user_routes.router)
app.include_router(project_routes.router)
app.include_router(task_routes.router)

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API de Gerenciamento de Projetos"}
