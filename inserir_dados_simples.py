from gestao_projetos.models.user import User
from gestao_projetos.models.project import Project
from gestao_projetos.models.task import Task
from gestao_projetos.core.database import SessionLocal
from datetime import datetime

db = SessionLocal()

# Criar usuários
user1 = User(name='João Silva', email='joao@exemplo.com')
user2 = User(name='Maria Oliveira', email='maria@exemplo.com')
user3 = User(name='Carlos Santos', email='carlos@exemplo.com')
db.add_all([user1, user2, user3])
db.commit()

# Buscar usuários criados
users = db.query(User).all()
print(f"Usuários criados: {len(users)}")
for user in users:
    print(f"  - {user.name} (ID: {user.id})")

# Criar projetos
project1 = Project(name='Sistema ERP', description='Desenvolvimento de sistema ERP completo', owner_id=users[0].id)
project2 = Project(name='App Mobile', description='Aplicativo móvel para gestão financeira', owner_id=users[1].id)
db.add_all([project1, project2])
db.commit()

# Buscar projetos criados
projects = db.query(Project).all()
print(f"\nProjetos criados: {len(projects)}")
for project in projects:
    print(f"  - {project.name} (ID: {project.id})")

print('\nDados de exemplo inseridos com sucesso!') 