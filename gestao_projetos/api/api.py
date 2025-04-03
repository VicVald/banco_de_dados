"""
Configuração principal da API
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from gestao_projetos.core.exceptions import GestaoProjetosException
from gestao_projetos.api import users, projects, tasks


# Criação da aplicação FastAPI
app = FastAPI(
    title="Gestão de Projetos API",
    description="API para gerenciamento de projetos e tarefas",
    version="1.0.0",
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


@app.get("/")
async def root():
    """
    Rota raiz da API.
    
    Retorna uma mensagem de boas-vindas.
    """
    return {"message": "Bem-vindo à API de Gestão de Projetos"} 