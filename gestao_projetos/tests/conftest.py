"""
Configuração dos testes com fixtures do pytest
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from gestao_projetos.core.database import Base


@pytest.fixture(scope="function")
def test_db():
    """
    Cria um banco de dados em memória para testes e fornece uma sessão
    
    Yields:
        Session: Uma sessão SQLAlchemy para o banco de dados de teste
    """
    # Conexão in-memory para testes
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Cria todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    # Sessão para testes
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        # Limpa as tabelas e fecha a sessão após o teste
        db.rollback()
        Base.metadata.drop_all(bind=engine)
        db.close()