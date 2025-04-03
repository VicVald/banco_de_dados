from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from app.models.project_model import Projects
from app.models.project_member_model import ProjectMembers
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectMemberCreate, ProjectMemberUpdate

class ProjectController:
    @staticmethod
    def get_project(db: Session, project_id: int):
        db_project = (
            db.query(Projects)
            .options(
                joinedload(Projects.owner),
                joinedload(Projects.members).joinedload(ProjectMembers.user)
            )
            .filter(Projects.id == project_id)
            .first()
        )
        
        if not db_project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado!")
        return db_project
    
    @staticmethod
    def create_project(db: Session, project: ProjectCreate):
        db_project = Projects(
            name=project.name,
            description=project.description,
            owner_id=project.owner_id
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def update_project(db: Session, project_id: int, project_data: ProjectUpdate):
        db_project = db.query(Projects).filter(Projects.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        for key, value in project_data.model_dump(exclude_unset=True).items():
            if value == 'string':
                continue
            setattr(db_project, key, value)
        
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def delete_project(db: Session, project_id: int):
        db_project = db.query(Projects).filter(Projects.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        db.delete(db_project)
        db.commit()
        return {"message": "Projeto apagado com sucesso"}
    
    @staticmethod
    def add_member(db: Session, project_id: int, member: ProjectMemberCreate):
        # Verificar se o projeto existe
        db_project = db.query(Projects).filter(Projects.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        # Verificar se o membro já existe
        existing_member = db.query(ProjectMembers).filter(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == member.user_id
        ).first()
        
        if existing_member:
            raise HTTPException(status_code=400, detail="Usuário já é membro deste projeto")
        
        # Adicionar novo membro
        db_member = ProjectMembers(
            project_id=project_id,
            user_id=member.user_id,
            role=member.role
        )
        
        db.add(db_member)
        db.commit()
        
        return {"status": "success", "message": "Membro adicionado com sucesso"}
    
    @staticmethod
    def update_member(db: Session, project_id: int, member_id: int, member_data: ProjectMemberUpdate):
        db_member = db.query(ProjectMembers).filter(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == member_id
        ).first()
        
        if not db_member:
            raise HTTPException(status_code=404, detail="Membro não encontrado neste projeto")
        
        for key, value in member_data.model_dump(exclude_unset=True).items():
            if value == 'string':
                continue
            setattr(db_member, key, value)
        
        db.commit()
        db.refresh(db_member)
        return db_member
    
    @staticmethod
    def delete_member(db: Session, project_id: int, member_id: int):
        db_member = db.query(ProjectMembers).filter(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == member_id
        ).first()
        
        if not db_member:
            raise HTTPException(status_code=404, detail="Membro não encontrado neste projeto")
        
        db.delete(db_member)
        db.commit()
        return {"message": "Membro removido com sucesso"} 