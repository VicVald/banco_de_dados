from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user_model import Users
from app.schemas.user_schema import UserCreate, UserUpdate

class UserController:
    @staticmethod
    def get_users(db: Session):
        users = db.query(Users).all()
        if not users:
            raise HTTPException(status_code=404, detail="Usuários não encontrados!")
        return users
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return user
    
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        db_user = Users(
            name=user.name,
            email=user.email
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate):
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
    
    @staticmethod
    def delete_user(db: Session, user_id: int):
        db_user = db.query(Users).filter(Users.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        db.delete(db_user)
        db.commit()
        return {"message": "Usuario Apagado com Sucesso"} 