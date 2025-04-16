# __________________
# Controlador responsável pelas operações CRUD relacionadas aos usuários
# __________________

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.userModels import Users
from ..main import UserBase, UserUpdate

# Obter todos os usuários cadastrados no banco de dados
def get_all_users(db: Session) -> List[Users]:
    result = db.query(Users).all()
    if not result:
        raise HTTPException(status_code=404, detail="Nenhum usuário encontrado")
    return result

# Criar um novo usuário no banco de dados
def create_new_user(user: UserBase, db: Session) -> Users:
    db_user = Users(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Atualizar informações de um usuário existente
def update_existing_user(user_id: int, user_data: UserUpdate, db: Session) -> Users:
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    for key, value in user_data.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# Deletar um usuário existente do banco de dados
def delete_existing_user(user_id: int, db: Session) -> dict:
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(db_user)
    db.commit()
    return {"message": "Usuário apagado com sucesso"}