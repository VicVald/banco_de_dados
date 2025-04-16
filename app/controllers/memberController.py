# __________________
# Controlador responsável pelas operações CRUD relacionadas aos membros dos projetos
# __________________

from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.userModels import ProjectMembers, Users, Projects
from ..main import ProjectMemberCreate, ProjectMemberUpdate

# Adicionar um novo membro a um projeto específico
def add_member_to_project(project_id: int, member: ProjectMemberCreate, db: Session):
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    db_user = db.query(Users).filter(Users.id == member.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db_member = ProjectMembers(project_id=project_id, user_id=member.user_id, role=member.role)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return {"message": "Membro adicionado com sucesso"}

# Atualizar informações de um membro existente em um projeto
def update_project_member(project_id: int, member_id: int, member: ProjectMemberUpdate, db: Session):
    db_member = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Membro não encontrado")

    for key, value in member.model_dump(exclude_unset=True).items():
        setattr(db_member, key, value)

    db.commit()
    db.refresh(db_member)
    return {"message": "Membro atualizado com sucesso"}

# Remover um membro existente de um projeto
def delete_project_member(project_id: int, member_id: int, db: Session):
    db_member = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Membro não encontrado")

    db.delete(db_member)
    db.commit()
    return {"message": "Membro removido com sucesso"}