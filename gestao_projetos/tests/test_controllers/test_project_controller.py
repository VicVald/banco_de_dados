"""
Testes para o ProjectController
"""
import pytest
from gestao_projetos.controllers.project_controller import ProjectController
from gestao_projetos.controllers.user_controller import UserController
from gestao_projetos.core.exceptions import (
    ResourceNotFoundException,
    NotProjectOwnerError,
    AlreadyProjectMemberError
)


def test_create_project(test_db):
    """Testa a criação de projeto"""
    # Criar usuário para teste
    user = UserController.create_user(test_db, name="Dono do Projeto", email="dono@example.com")
    
    # Criar projeto
    project = ProjectController.create_project(
        test_db, 
        name="Projeto Teste", 
        owner_id=user.id, 
        description="Descrição do projeto de teste"
    )
    
    # Verificar se o projeto foi criado corretamente
    assert project.id is not None
    assert project.name == "Projeto Teste"
    assert project.description == "Descrição do projeto de teste"
    assert project.owner_id == user.id


def test_add_member(test_db):
    """Testa a adição de um membro ao projeto"""
    # Criar usuários para teste
    owner = UserController.create_user(test_db, name="Dono", email="dono@example.com")
    member = UserController.create_user(test_db, name="Membro", email="membro@example.com")
    
    # Criar projeto
    project = ProjectController.create_project(
        test_db, 
        name="Projeto com Membros", 
        owner_id=owner.id
    )
    
    # Adicionar membro
    project_member = ProjectController.add_member(
        test_db,
        project_id=project.id,
        user_id=owner.id,
        member_user_id=member.id,
        role="desenvolvedor"
    )
    
    # Verificar se o membro foi adicionado corretamente
    assert project_member.project_id == project.id
    assert project_member.user_id == member.id
    assert project_member.role == "desenvolvedor"
    
    # Tentar adicionar o mesmo membro novamente (deve falhar)
    with pytest.raises(AlreadyProjectMemberError):
        ProjectController.add_member(
            test_db,
            project_id=project.id,
            user_id=owner.id,
            member_user_id=member.id
        )


def test_project_ownership_validation(test_db):
    """Testa a validação de proprietário do projeto"""
    # Criar usuários para teste
    owner = UserController.create_user(test_db, name="Dono", email="dono@example.com")
    non_owner = UserController.create_user(test_db, name="Não Dono", email="nao_dono@example.com")
    
    # Criar projeto
    project = ProjectController.create_project(
        test_db, 
        name="Projeto Protegido", 
        owner_id=owner.id
    )
    
    # Usuário não proprietário tenta deletar o projeto (deve falhar)
    with pytest.raises(NotProjectOwnerError):
        ProjectController.delete_project(test_db, project.id, non_owner.id)
    
    # Proprietário tenta deletar (deve funcionar)
    result = ProjectController.delete_project(test_db, project.id, owner.id)
    assert result is True 