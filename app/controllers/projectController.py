# __________________
# Controlador responsável pelas operações CRUD relacionadas aos projetos
# __________________

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..models.userModels import Projects, ProjectMembers, Users # Assuming models are in userModels for now
from ..main import ProjectBase, ProjectUpdate, ProjectResponse # Import Pydantic models

# Obter detalhes de um projeto específico pelo ID
def get_project_by_id(project_id: int, db: Session) -> ProjectResponse:
    db_project = (
        db.query(Projects)
        .options(
            joinedload(Projects.owner),
            joinedload(Projects.members).joinedload(ProjectMembers.user) # Eager load relations
        )
        .filter(Projects.id == project_id)
        .first()
    )
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return db_project

# Criar um novo projeto no banco de dados
def create_new_project(project: ProjectBase, db: Session) -> Projects:
     # Add validation if owner_id exists?
    db_owner = db.query(Users).filter(Users.id == project.owner_id).first()
    if not db_owner:
         raise HTTPException(status_code=404, detail=f"Usuário proprietário com id {project.owner_id} não encontrado")

    db_project = Projects(
        name=project.name,
        description=project.description,
        owner_id=project.owner_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    # Add the owner as a member automatically? Or handle separately?
    # For now, just return the created project
    return db_project

# Atualizar informações de um projeto existente
def update_existing_project(project_id: int, project_data: ProjectUpdate, db: Session) -> Projects:
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    update_data = project_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        # Add validation if owner_id is being changed?
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project

# Deletar um projeto existente do banco de dados
def delete_existing_project(project_id: int, db: Session) -> dict:
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    # Consider deleting related members and tasks or handle constraints
    db.delete(db_project)
    db.commit()
    return {"message": "Projeto apagado com sucesso"}