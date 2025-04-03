"""
Configuração principal da API
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from gestao_projetos.core.exceptions import GestaoProjetosException
from gestao_projetos.api import users, projects, tasks


# Criação da aplicação FastAPI
app = FastAPI(
    title="Gestão de Projetos API",
    description="API para gerenciamento de projetos e tarefas",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens em ambiente de desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os headers
)

# Incluir rotas de cada módulo
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)


# Handler global para exceções personalizadas
@app.exception_handler(GestaoProjetosException)
async def gestao_projetos_exception_handler(request: Request, exc: GestaoProjetosException):
    """
    Manipulador de exceções personalizadas do sistema.
    
    Retorna uma resposta JSON com detalhes do erro.
    """
    status_code = 400  # Bad request por padrão
    
    # Ajusta o status code conforme o tipo de exceção
    if isinstance(exc, GestaoProjetosException):
        if "não encontrado" in exc.message:
            status_code = status.HTTP_404_NOT_FOUND
        elif "não autorizado" in exc.message or "não é dono" in exc.message:
            status_code = status.HTTP_403_FORBIDDEN
        
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": exc.message,
            "status_code": status_code,
            "error_type": exc.__class__.__name__
        },
    )


# Montar arquivos estáticos
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """
    Rota raiz da API - Retorna a interface gráfica.
    """
    return FileResponse(os.path.join(static_dir, 'index.html'))


@app.get("/api")
async def api_info():
    """
    Informações sobre a API.
    
    Retorna uma mensagem de boas-vindas.
    """
    return {"message": "Bem-vindo à API de Gestão de Projetos"} 