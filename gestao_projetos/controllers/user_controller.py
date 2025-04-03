"""
Controller de usuários
"""
from sqlalchemy.orm import Session
from gestao_projetos.models.user import User
from gestao_projetos.core.exceptions import ResourceNotFoundException


class UserController:
    """
    Controller para gerenciamento de usuários.
    
    Implementa a lógica de negócio relacionada a usuários.
    """
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        """
        Obtém a lista de usuários.
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular (para paginação)
            limit: Número máximo de registros a retornar
            
        Returns:
            list: Lista de usuários
        """
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        """
        Obtém um usuário pelo ID.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            
        Returns:
            User: Usuário encontrado
            
        Raises:
            ResourceNotFoundException: Se o usuário não for encontrado
        """
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise ResourceNotFoundException("Usuário", user_id)
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        """
        Obtém um usuário pelo email.
        
        Args:
            db: Sessão do banco de dados
            email: Email do usuário
            
        Returns:
            User: Usuário encontrado ou None se não encontrado
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, name: str, email: str):
        """
        Cria um novo usuário.
        
        Args:
            db: Sessão do banco de dados
            name: Nome do usuário
            email: Email do usuário
            
        Returns:
            User: Usuário criado
        """
        user = User(name=name, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs):
        """
        Atualiza os dados de um usuário.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            **kwargs: Campos a serem atualizados
            
        Returns:
            User: Usuário atualizado
            
        Raises:
            ResourceNotFoundException: Se o usuário não for encontrado
        """
        user = UserController.get_user_by_id(db, user_id)
        
        # Atualiza apenas os campos fornecidos
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int):
        """
        Remove um usuário.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            
        Returns:
            bool: True se o usuário foi removido, False caso contrário
            
        Raises:
            ResourceNotFoundException: Se o usuário não for encontrado
        """
        user = UserController.get_user_by_id(db, user_id)
        db.delete(user)
        db.commit()
        return True 