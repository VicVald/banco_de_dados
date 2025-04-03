"""
Testes para o modelo de Tarefas
"""
import pytest
from sqlalchemy.exc import IntegrityError
from gestao_projetos.models.user import User
from gestao_projetos.models.project import Project
from gestao_projetos.models.task import Task
from gestao_projetos.core.exceptions import InvalidTaskStateError


def test_task_number_uniqueness(test_db):
    """Testa que não é possível ter duas tarefas com o mesmo número em um projeto"""
    # Criar usuário, projeto e tarefas para teste
    user = User(name="Testador", email="testador@example.com")
    test_db.add(user)
    test_db.commit()
    
    project = Project(name="Projeto Teste", owner_id=user.id)
    test_db.add(project)
    test_db.commit()
    
    # Primeira tarefa (deve funcionar)
    task1 = Task(
        project_id=project.id,
        task_number=1,
        title="Tarefa 1",
        description="Descrição da tarefa 1",
        state="backlog"
    )
    test_db.add(task1)
    test_db.commit()
    
    # Segunda tarefa com mesmo número (deve falhar)
    task2 = Task(
        project_id=project.id,
        task_number=1,  # Mesmo número da tarefa anterior
        title="Tarefa Duplicada",
        description="Esta tarefa tem número duplicado",
        state="backlog"
    )
    test_db.add(task2)
    
    # Deve lançar IntegrityError ao tentar commit por causa da UniqueConstraint
    with pytest.raises(IntegrityError):
        test_db.commit()


def test_task_state_machine(test_db):
    """Testa a máquina de estados da tarefa"""
    # Criar usuário, projeto e tarefa para teste
    user = User(name="Testador", email="testador@example.com")
    test_db.add(user)
    test_db.commit()
    
    project = Project(name="Projeto Teste", owner_id=user.id)
    test_db.add(project)
    test_db.commit()
    
    task = Task(
        project_id=project.id,
        task_number=1,
        title="Tarefa Estado",
        description="Teste de máquina de estado",
        state="backlog"
    )
    test_db.add(task)
    test_db.commit()
    
    # Transição válida: backlog -> em_progresso
    task.change_state("em_progresso")
    test_db.commit()
    assert task.state == "em_progresso"
    
    # Transição inválida: em_progresso -> concluida (deve passar por em_revisao)
    with pytest.raises(InvalidTaskStateError):
        task.change_state("concluida")
    
    # Transição válida: em_progresso -> em_revisao
    task.change_state("em_revisao")
    test_db.commit()
    assert task.state == "em_revisao"
    
    # Transição válida: em_revisao -> concluida
    task.change_state("concluida")
    test_db.commit()
    assert task.state == "concluida"
    
    # Estado inválido
    with pytest.raises(InvalidTaskStateError):
        task.change_state("estado_invalido") 