"""
Aplicação principal para iniciar o servidor FastAPI
"""
import uvicorn
from gestao_projetos.api.api import app
from gestao_projetos.core.database import Base, engine

# Cria todas as tabelas definidas nos modelos
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 