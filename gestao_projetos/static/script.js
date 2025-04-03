// Configuração da API
const API_URL = 'http://localhost:8000';

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Navegação entre seções
    const navLinks = document.querySelectorAll('nav a');
    const sections = document.querySelectorAll('section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remover classe active de todos os links e seções
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // Adicionar classe active ao link clicado e à seção correspondente
            this.classList.add('active');
            const sectionId = this.getAttribute('data-section');
            document.getElementById(sectionId).classList.add('active');
        });
    });
    
    // Modal
    const modal = document.getElementById('modal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
    
    // Carregar dados iniciais
    loadUsers();
    loadProjects();
    
    // Event Listeners para formulários
    document.getElementById('addUserForm').addEventListener('submit', addUser);
    document.getElementById('addProjectForm').addEventListener('submit', addProject);
    document.getElementById('addTaskForm').addEventListener('submit', addTask);
    document.getElementById('filterProject').addEventListener('change', filterTasks);
});

// Funções de gerenciamento de usuários
async function loadUsers() {
    try {
        const response = await fetch(`${API_URL}/users/`);
        const users = await response.json();
        
        // Preencher a lista de usuários
        const usersList = document.getElementById('usersList');
        usersList.innerHTML = '';
        
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td class="action-buttons">
                    <button class="btn-view" onclick="viewUser(${user.id})">Ver</button>
                    <button class="btn-edit" onclick="editUser(${user.id})">Editar</button>
                    <button class="btn-delete" onclick="deleteUser(${user.id})">Excluir</button>
                </td>
            `;
            usersList.appendChild(row);
        });
        
        // Preencher os selects de usuários em outros formulários
        const projectOwnerSelect = document.getElementById('projectOwner');
        const taskAssigneeSelect = document.getElementById('taskAssignee');
        
        projectOwnerSelect.innerHTML = '';
        taskAssigneeSelect.innerHTML = '<option value="">Ninguém</option>';
        
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.name;
            
            const option2 = option.cloneNode(true);
            
            projectOwnerSelect.appendChild(option);
            taskAssigneeSelect.appendChild(option2);
        });
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
        alert('Não foi possível carregar a lista de usuários. Verifique se a API está em execução.');
    }
}

async function addUser(e) {
    e.preventDefault();
    
    const name = document.getElementById('userName').value;
    const email = document.getElementById('userEmail').value;
    
    try {
        const response = await fetch(`${API_URL}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email })
        });
        
        if (response.ok) {
            // Limpar formulário e recarregar usuários
            document.getElementById('addUserForm').reset();
            loadUsers();
            alert('Usuário adicionado com sucesso!');
        } else {
            const data = await response.json();
            alert(`Erro: ${data.detail}`);
        }
    } catch (error) {
        console.error('Erro ao adicionar usuário:', error);
        alert('Não foi possível adicionar o usuário. Verifique se a API está em execução.');
    }
}

async function viewUser(id) {
    try {
        const response = await fetch(`${API_URL}/users/${id}`);
        const user = await response.json();
        
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `Usuário: ${user.name}`;
        modalBody.innerHTML = `
            <p><strong>ID:</strong> ${user.id}</p>
            <p><strong>Nome:</strong> ${user.name}</p>
            <p><strong>Email:</strong> ${user.email}</p>
            <p><strong>Status:</strong> ${user.is_active ? 'Ativo' : 'Inativo'}</p>
        `;
        
        document.getElementById('modal').style.display = 'block';
    } catch (error) {
        console.error('Erro ao carregar detalhes do usuário:', error);
        alert('Não foi possível carregar os detalhes do usuário.');
    }
}

async function editUser(id) {
    try {
        const response = await fetch(`${API_URL}/users/${id}`);
        const user = await response.json();
        
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `Editar Usuário: ${user.name}`;
        modalBody.innerHTML = `
            <form id="editUserForm">
                <div class="form-group">
                    <label for="editUserName">Nome:</label>
                    <input type="text" id="editUserName" value="${user.name}" required>
                </div>
                <div class="form-group">
                    <label for="editUserEmail">Email:</label>
                    <input type="email" id="editUserEmail" value="${user.email}" required>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="editUserActive" ${user.is_active ? 'checked' : ''}>
                        Ativo
                    </label>
                </div>
                <button type="submit">Salvar Alterações</button>
            </form>
        `;
        
        document.getElementById('modal').style.display = 'block';
        
        // Adicionar event listener para o formulário de edição
        document.getElementById('editUserForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('editUserName').value;
            const email = document.getElementById('editUserEmail').value;
            const is_active = document.getElementById('editUserActive').checked;
            
            try {
                const updateResponse = await fetch(`${API_URL}/users/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, email, is_active })
                });
                
                if (updateResponse.ok) {
                    document.getElementById('modal').style.display = 'none';
                    loadUsers();
                    alert('Usuário atualizado com sucesso!');
                } else {
                    const data = await updateResponse.json();
                    alert(`Erro: ${data.detail}`);
                }
            } catch (error) {
                console.error('Erro ao atualizar usuário:', error);
                alert('Não foi possível atualizar o usuário.');
            }
        });
    } catch (error) {
        console.error('Erro ao carregar detalhes do usuário para edição:', error);
        alert('Não foi possível carregar os detalhes do usuário.');
    }
}

async function deleteUser(id) {
    if (confirm('Tem certeza de que deseja excluir este usuário?')) {
        try {
            const response = await fetch(`${API_URL}/users/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                loadUsers();
                alert('Usuário excluído com sucesso!');
            } else {
                const data = await response.json();
                alert(`Erro: ${data.detail}`);
            }
        } catch (error) {
            console.error('Erro ao excluir usuário:', error);
            alert('Não foi possível excluir o usuário.');
        }
    }
}

// Funções de gerenciamento de projetos
async function loadProjects() {
    try {
        const response = await fetch(`${API_URL}/projects/`);
        const projects = await response.json();
        
        // Preencher a lista de projetos
        const projectsList = document.getElementById('projectsList');
        projectsList.innerHTML = '';
        
        projects.forEach(project => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${project.id}</td>
                <td>${project.name}</td>
                <td>${project.owner ? project.owner.name : 'N/A'}</td>
                <td class="action-buttons">
                    <button class="btn-view" onclick="viewProject(${project.id})">Ver</button>
                    <button class="btn-edit" onclick="editProject(${project.id})">Editar</button>
                    <button class="btn-delete" onclick="deleteProject(${project.id})">Excluir</button>
                </td>
            `;
            projectsList.appendChild(row);
        });
        
        // Preencher o select de projetos no formulário de tarefas
        const taskProjectSelect = document.getElementById('taskProject');
        const filterProjectSelect = document.getElementById('filterProject');
        
        taskProjectSelect.innerHTML = '';
        filterProjectSelect.innerHTML = '<option value="">Todos os projetos</option>';
        
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            
            const option2 = option.cloneNode(true);
            
            taskProjectSelect.appendChild(option);
            filterProjectSelect.appendChild(option2);
        });
        
        // Carregar tarefas após carregar projetos
        loadTasks();
    } catch (error) {
        console.error('Erro ao carregar projetos:', error);
        alert('Não foi possível carregar a lista de projetos. Verifique se a API está em execução.');
    }
}

async function addProject(e) {
    e.preventDefault();
    
    const name = document.getElementById('projectName').value;
    const description = document.getElementById('projectDescription').value;
    const owner_id = parseInt(document.getElementById('projectOwner').value);
    
    try {
        const response = await fetch(`${API_URL}/projects/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, description, owner_id })
        });
        
        if (response.ok) {
            // Limpar formulário e recarregar projetos
            document.getElementById('addProjectForm').reset();
            loadProjects();
            alert('Projeto adicionado com sucesso!');
        } else {
            const data = await response.json();
            alert(`Erro: ${data.detail}`);
        }
    } catch (error) {
        console.error('Erro ao adicionar projeto:', error);
        alert('Não foi possível adicionar o projeto. Verifique se a API está em execução.');
    }
}

async function viewProject(id) {
    try {
        const response = await fetch(`${API_URL}/projects/${id}`);
        const project = await response.json();
        
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `Projeto: ${project.name}`;
        
        let membersHTML = '<p>Sem membros</p>';
        if (project.members && project.members.length > 0) {
            membersHTML = '<ul>';
            project.members.forEach(member => {
                membersHTML += `<li>${member.user.name} (${member.role})</li>`;
            });
            membersHTML += '</ul>';
        }
        
        modalBody.innerHTML = `
            <p><strong>ID:</strong> ${project.id}</p>
            <p><strong>Nome:</strong> ${project.name}</p>
            <p><strong>Descrição:</strong> ${project.description || 'Sem descrição'}</p>
            <p><strong>Dono:</strong> ${project.owner ? project.owner.name : 'N/A'}</p>
            <p><strong>Criado em:</strong> ${new Date(project.created_at).toLocaleString()}</p>
            <h3>Membros:</h3>
            ${membersHTML}
        `;
        
        document.getElementById('modal').style.display = 'block';
    } catch (error) {
        console.error('Erro ao carregar detalhes do projeto:', error);
        alert('Não foi possível carregar os detalhes do projeto.');
    }
}

// Funções de gerenciamento de tarefas
async function loadTasks(projectFilter = '') {
    try {
        let url = `${API_URL}/tasks`;
        if (projectFilter) {
            url = `${API_URL}/tasks/project/${projectFilter}`;
        }
        
        const response = await fetch(url);
        const tasks = await response.json();
        
        // Preencher a lista de tarefas
        const tasksList = document.getElementById('tasksList');
        tasksList.innerHTML = '';
        
        tasks.forEach(task => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${task.id}</td>
                <td>${task.task_number}</td>
                <td>${task.title}</td>
                <td>${task.project ? task.project.name : 'N/A'}</td>
                <td><span class="status-badge status-${task.state}">${task.state}</span></td>
                <td>${task.assigned_user ? task.assigned_user.name : 'Não atribuído'}</td>
                <td class="action-buttons">
                    <button class="btn-view" onclick="viewTask(${task.id})">Ver</button>
                    <button class="btn-edit" onclick="editTask(${task.id})">Editar</button>
                    <button class="btn-delete" onclick="deleteTask(${task.id})">Excluir</button>
                </td>
            `;
            tasksList.appendChild(row);
        });
    } catch (error) {
        console.error('Erro ao carregar tarefas:', error);
        // Não mostrar alerta aqui, pois pode não haver tarefas ainda
    }
}

async function addTask(e) {
    e.preventDefault();
    
    const title = document.getElementById('taskTitle').value;
    const description = document.getElementById('taskDescription').value;
    const project_id = parseInt(document.getElementById('taskProject').value);
    const user_id = document.getElementById('taskAssignee').value ? parseInt(document.getElementById('taskAssignee').value) : null;
    
    try {
        const response = await fetch(`${API_URL}/tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                title, 
                description, 
                project_id, 
                user_id,
                state: 'backlog'
            })
        });
        
        if (response.ok) {
            // Limpar formulário e recarregar tarefas
            document.getElementById('addTaskForm').reset();
            loadTasks();
            alert('Tarefa adicionada com sucesso!');
        } else {
            const data = await response.json();
            alert(`Erro: ${data.detail}`);
        }
    } catch (error) {
        console.error('Erro ao adicionar tarefa:', error);
        alert('Não foi possível adicionar a tarefa. Verifique se a API está em execução.');
    }
}

function filterTasks() {
    const projectId = document.getElementById('filterProject').value;
    loadTasks(projectId);
}

async function editProject(id) {
    try {
        const response = await fetch(`${API_URL}/projects/${id}`);
        const project = await response.json();
        
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `Editar Projeto: ${project.name}`;
        modalBody.innerHTML = `
            <form id="editProjectForm">
                <div class="form-group">
                    <label for="editProjectName">Nome:</label>
                    <input type="text" id="editProjectName" value="${project.name}" required>
                </div>
                <div class="form-group">
                    <label for="editProjectDescription">Descrição:</label>
                    <textarea id="editProjectDescription">${project.description || ''}</textarea>
                </div>
                <div class="form-group">
                    <label for="editProjectOwner">Dono:</label>
                    <select id="editProjectOwner">
                        <!-- Será preenchido via JavaScript -->
                    </select>
                </div>
                <button type="submit">Salvar Alterações</button>
            </form>
        `;
        
        document.getElementById('modal').style.display = 'block';
        
        // Carregar usuários para o select
        const ownerSelect = document.getElementById('editProjectOwner');
        const usersResponse = await fetch(`${API_URL}/users/`);
        const users = await usersResponse.json();
        
        ownerSelect.innerHTML = '';
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.name;
            if (project.owner && user.id === project.owner.id) {
                option.selected = true;
            }
            ownerSelect.appendChild(option);
        });
        
        // Adicionar event listener para o formulário de edição
        document.getElementById('editProjectForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('editProjectName').value;
            const description = document.getElementById('editProjectDescription').value;
            const owner_id = parseInt(document.getElementById('editProjectOwner').value);
            
            try {
                const updateResponse = await fetch(`${API_URL}/projects/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, description, owner_id })
                });
                
                if (updateResponse.ok) {
                    document.getElementById('modal').style.display = 'none';
                    loadProjects();
                    alert('Projeto atualizado com sucesso!');
                } else {
                    const data = await updateResponse.json();
                    alert(`Erro: ${data.detail}`);
                }
            } catch (error) {
                console.error('Erro ao atualizar projeto:', error);
                alert('Não foi possível atualizar o projeto.');
            }
        });
    } catch (error) {
        console.error('Erro ao carregar detalhes do projeto para edição:', error);
        alert('Não foi possível carregar os detalhes do projeto.');
    }
}

async function deleteProject(id) {
    if (confirm('Tem certeza de que deseja excluir este projeto?')) {
        try {
            const response = await fetch(`${API_URL}/projects/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                loadProjects();
                alert('Projeto excluído com sucesso!');
            } else {
                const data = await response.json();
                alert(`Erro: ${data.detail}`);
            }
        } catch (error) {
            console.error('Erro ao excluir projeto:', error);
            alert('Não foi possível excluir o projeto.');
        }
    }
}

async function viewTask(id) {
    try {
        const response = await fetch(`${API_URL}/tasks/${id}`);
        const task = await response.json();
        
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `Tarefa: ${task.title}`;
        
        modalBody.innerHTML = `
            <p><strong>ID:</strong> ${task.id}</p>
            <p><strong>Número:</strong> ${task.task_number}</p>
            <p><strong>Título:</strong> ${task.title}</p>
            <p><strong>Descrição:</strong> ${task.description || 'Sem descrição'}</p>
            <p><strong>Projeto:</strong> ${task.project ? task.project.name : 'N/A'}</p>
            <p><strong>Estado:</strong> <span class="status-badge status-${task.state}">${task.state}</span></p>
            <p><strong>Atribuído a:</strong> ${task.assigned_user ? task.assigned_user.name : 'Não atribuído'}</p>
            <p><strong>Criado em:</strong> ${new Date(task.created_at).toLocaleString()}</p>
            
            <div class="task-actions">
                <h3>Mudar estado:</h3>
                <div class="state-buttons">
                    <button onclick="changeTaskState(${task.id}, 'backlog')" class="state-btn backlog">Backlog</button>
                    <button onclick="changeTaskState(${task.id}, 'in_progress')" class="state-btn in-progress">Em Progresso</button>
                    <button onclick="changeTaskState(${task.id}, 'under_review')" class="state-btn under-review">Em Revisão</button>
                    <button onclick="changeTaskState(${task.id}, 'done')" class="state-btn done">Concluído</button>
                </div>
            </div>
        `;
        
        document.getElementById('modal').style.display = 'block';
    } catch (error) {
        console.error('Erro ao carregar detalhes da tarefa:', error);
        alert('Não foi possível carregar os detalhes da tarefa.');
    }
}

async function editTask(id) {
    try {
        const response = await fetch(`${API_URL}/tasks/${id}`);
        const task = await response.json();
        
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `Editar Tarefa: ${task.title}`;
        modalBody.innerHTML = `
            <form id="editTaskForm">
                <div class="form-group">
                    <label for="editTaskTitle">Título:</label>
                    <input type="text" id="editTaskTitle" value="${task.title}" required>
                </div>
                <div class="form-group">
                    <label for="editTaskDescription">Descrição:</label>
                    <textarea id="editTaskDescription">${task.description || ''}</textarea>
                </div>
                <div class="form-group">
                    <label for="editTaskProject">Projeto:</label>
                    <select id="editTaskProject" required>
                        <!-- Será preenchido via JavaScript -->
                    </select>
                </div>
                <div class="form-group">
                    <label for="editTaskAssignee">Atribuído a:</label>
                    <select id="editTaskAssignee">
                        <option value="">Ninguém</option>
                        <!-- Será preenchido via JavaScript -->
                    </select>
                </div>
                <div class="form-group">
                    <label for="editTaskState">Estado:</label>
                    <select id="editTaskState" required>
                        <option value="backlog" ${task.state === 'backlog' ? 'selected' : ''}>Backlog</option>
                        <option value="in_progress" ${task.state === 'in_progress' ? 'selected' : ''}>Em Progresso</option>
                        <option value="under_review" ${task.state === 'under_review' ? 'selected' : ''}>Em Revisão</option>
                        <option value="done" ${task.state === 'done' ? 'selected' : ''}>Concluído</option>
                    </select>
                </div>
                <button type="submit">Salvar Alterações</button>
            </form>
        `;
        
        document.getElementById('modal').style.display = 'block';
        
        // Carregar projetos para o select
        const projectSelect = document.getElementById('editTaskProject');
        const projectsResponse = await fetch(`${API_URL}/projects/`);
        const projects = await projectsResponse.json();
        
        projectSelect.innerHTML = '';
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            if (task.project && project.id === task.project.id) {
                option.selected = true;
            }
            projectSelect.appendChild(option);
        });
        
        // Carregar usuários para o select
        const assigneeSelect = document.getElementById('editTaskAssignee');
        const usersResponse = await fetch(`${API_URL}/users/`);
        const users = await usersResponse.json();
        
        assigneeSelect.innerHTML = '<option value="">Ninguém</option>';
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.name;
            if (task.assigned_user && user.id === task.assigned_user.id) {
                option.selected = true;
            }
            assigneeSelect.appendChild(option);
        });
        
        // Adicionar event listener para o formulário de edição
        document.getElementById('editTaskForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const title = document.getElementById('editTaskTitle').value;
            const description = document.getElementById('editTaskDescription').value;
            const project_id = parseInt(document.getElementById('editTaskProject').value);
            const user_id = document.getElementById('editTaskAssignee').value ? parseInt(document.getElementById('editTaskAssignee').value) : null;
            const state = document.getElementById('editTaskState').value;
            
            try {
                const updateResponse = await fetch(`${API_URL}/tasks/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ title, description, project_id, user_id, state })
                });
                
                if (updateResponse.ok) {
                    document.getElementById('modal').style.display = 'none';
                    loadTasks(document.getElementById('filterProject').value);
                    alert('Tarefa atualizada com sucesso!');
                } else {
                    const data = await updateResponse.json();
                    alert(`Erro: ${data.detail}`);
                }
            } catch (error) {
                console.error('Erro ao atualizar tarefa:', error);
                alert('Não foi possível atualizar a tarefa.');
            }
        });
    } catch (error) {
        console.error('Erro ao carregar detalhes da tarefa para edição:', error);
        alert('Não foi possível carregar os detalhes da tarefa.');
    }
}

async function deleteTask(id) {
    if (confirm('Tem certeza de que deseja excluir esta tarefa?')) {
        try {
            const response = await fetch(`${API_URL}/tasks/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                loadTasks(document.getElementById('filterProject').value);
                alert('Tarefa excluída com sucesso!');
            } else {
                const data = await response.json();
                alert(`Erro: ${data.detail}`);
            }
        } catch (error) {
            console.error('Erro ao excluir tarefa:', error);
            alert('Não foi possível excluir a tarefa.');
        }
    }
}

async function changeTaskState(id, newState) {
    try {
        const response = await fetch(`${API_URL}/tasks/${id}/state`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ state: newState })
        });
        
        if (response.ok) {
            document.getElementById('modal').style.display = 'none';
            loadTasks(document.getElementById('filterProject').value);
            alert('Estado da tarefa atualizado com sucesso!');
        } else {
            const data = await response.json();
            alert(`Erro: ${data.detail}`);
        }
    } catch (error) {
        console.error('Erro ao mudar estado da tarefa:', error);
        alert('Não foi possível mudar o estado da tarefa.');
    }
} 