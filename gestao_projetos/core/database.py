"""
Módulo de configuração do banco de dados SQLite com SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# URL de conexão SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'gestao_projetos.db')}"

# Criação do engine SQLAlchemy com configurações específicas para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Necessário apenas para SQLite
)

# Criação da sessão do SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para as classes de modelo
Base = declarative_base()

def get_db():
    """
    Função para obter uma sessão do banco de dados.
    Utiliza pattern de context manager para garantir que a sessão seja fechada após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 