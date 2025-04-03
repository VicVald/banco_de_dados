# Sistema de Gestão de Projetos (MVC)

Este é um sistema de gestão de projetos e tarefas desenvolvido com Python, FastAPI e SQLAlchemy, seguindo a arquitetura MVC (Model-View-Controller).

## Estrutura do Projeto

O projeto está organizado em uma estrutura MVC escalável:

```
gestao_projetos/  
├── core/                     # Configurações globais  
│   ├── database.py           # Conexão SQLite + Base do SQLAlchemy  
│   └── exceptions.py         # Custom exceptions  
├── models/                   # Entidades da MER  
│   ├── user.py               # Modelo User + métodos de owner validation  
│   ├── project.py            # Modelo Project + CRUD básico  
│   ├── task.py               # Modelo Task + UniqueConstraint  
│   └── member.py             # Modelo ProjectMembers (N:M)  
├── controllers/              # Lógica de negócio  
│   ├── user_controller.py    # User management + auth  
│   ├── project_controller.py # Project/member operations  
│   └── task_controller.py    # Task state machine + numbering  
├── api/                      # Endpoints (FastAPI)  
│   ├── schemas.py            # Pydantic models (validação)  
│   ├── api.py                # Configuração principal da API
│   ├── users.py              # Rotas de usuários
│   ├── projects.py           # Rotas de projetos
│   └── tasks.py              # Rotas de tarefas
└── tests/                    # Testes por camada  
    ├── test_models/          # Testes de relações + constraints  
    └── test_controllers/     # Testes de regras de negócio  
```

## Recursos Implementados

- **Modelos com Relacionamentos**:
  - Usuários (1:N com Projetos)
  - Projetos (1:N com Tarefas)
  - Membros do Projeto (N:M entre Usuários e Projetos)
  - Tarefas com numeração automática por projeto

- **Validações e Constraints**:
  - Número único de tarefa por projeto
  - Máquina de estado para tarefas
  - Verificação de propriedade de projetos

- **Tratamento de Erros**:
  - Exceções customizadas
  - Resposta com status HTTP apropriados

## Instalação

1. Clone o repositório:
```bash
git clone <repositório>
cd gestao-projetos
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

Execute o servidor de desenvolvimento:

```bash
python main.py
```

A API estará disponível em `http://localhost:8000`. A documentação interativa Swagger UI estará disponível em `http://localhost:8000/docs`.

## Testes

Execute os testes automatizados:

```bash
pytest
```

## Documentação da API

A documentação completa da API está disponível em:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc