from gestao_projetos.models.user import User
from gestao_projetos.models.project import Project
from gestao_projetos.models.task import Task
from gestao_projetos.models.member import ProjectMember
from gestao_projetos.core.database import SessionLocal, Base, engine
from datetime import datetime

# Criar todas as tabelas
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Limpar dados existentes
db.query(Task).delete()
db.query(ProjectMember).delete()
db.query(Project).delete()
db.query(User).delete()
db.commit()

# Criar usuários
user1 = User(name='João Silva', email='joao@exemplo.com')
user2 = User(name='Maria Oliveira', email='maria@exemplo.com')
user3 = User(name='Carlos Santos', email='carlos@exemplo.com')
db.add_all([user1, user2, user3])
db.commit()

# Buscar usuários para usar nos projetos
users = db.query(User).all()

# Criar projetos
project1 = Project(name='Sistema ERP', description='Desenvolvimento de sistema ERP completo', owner_id=users[0].id)
project2 = Project(name='App Mobile', description='Aplicativo móvel para gestão financeira', owner_id=users[1].id)
db.add_all([project1, project2])
db.commit()

# Buscar projetos para usar nas tarefas
projects = db.query(Project).all()

# Criar tarefas
task1 = Task(
    title='Implementar login', 
    description='Criar sistema de autenticação', 
    project_id=projects[0].id, 
    user_id=users[0].id, 
    state='backlog',
    task_number=1
)
task2 = Task(
    title='Criar dashboard', 
    description='Desenvolver dashboard administrativo', 
    project_id=projects[0].id, 
    user_id=users[1].id, 
    state='in_progress',
    task_number=2
)
task3 = Task(
    title='Desenhar interface', 
    description='Criar wireframes do app', 
    project_id=projects[1].id, 
    user_id=users[1].id, 
    state='done',
    task_number=1
)
task4 = Task(
    title='Implementar API', 
    description='Desenvolver endpoints da API', 
    project_id=projects[1].id, 
    user_id=users[2].id, 
    state='under_review',
    task_number=2
)
task5 = Task(
    title='Testes unitários', 
    description='Escrever testes para o sistema', 
    project_id=projects[0].id, 
    user_id=users[2].id, 
    state='backlog',
    task_number=3
)
db.add_all([task1, task2, task3, task4, task5])
db.commit()

# Adicionar membros aos projetos
member1 = ProjectMember(project_id=projects[0].id, user_id=users[1].id, role="desenvolvedor")
member2 = ProjectMember(project_id=projects[0].id, user_id=users[2].id, role="tester")
member3 = ProjectMember(project_id=projects[1].id, user_id=users[0].id, role="analista")
member4 = ProjectMember(project_id=projects[1].id, user_id=users[2].id, role="desenvolvedor")
db.add_all([member1, member2, member3, member4])
db.commit()

print('Dados de exemplo inseridos com sucesso!') 