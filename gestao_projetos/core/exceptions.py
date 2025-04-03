"""
Exceções personalizadas para o sistema de gestão de projetos
"""

class GestaoProjetosException(Exception):
    """Exceção base para o sistema de gestão de projetos"""
    def __init__(self, message="Erro no sistema de gestão de projetos"):
        self.message = message
        super().__init__(self.message)


class ResourceNotFoundException(GestaoProjetosException):
    """Exceção lançada quando um recurso não é encontrado"""
    def __init__(self, resource_type, resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.message = f"{resource_type} com ID {resource_id} não encontrado(a)."
        super().__init__(self.message)


class TaskNumberDuplicateError(GestaoProjetosException):
    """Exceção lançada quando há tentativa de criar tarefa com número duplicado no projeto"""
    def __init__(self, project_id, task_number):
        self.project_id = project_id
        self.task_number = task_number
        self.message = f"Já existe uma tarefa com número {task_number} no projeto {project_id}."
        super().__init__(self.message)


class NotProjectOwnerError(GestaoProjetosException):
    """Exceção lançada quando um usuário tenta realizar operação sem ser dono do projeto"""
    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id
        self.message = f"Usuário {user_id} não é dono do projeto {project_id} e não pode realizar esta operação."
        super().__init__(self.message)


class AlreadyProjectMemberError(GestaoProjetosException):
    """Exceção lançada quando tenta-se adicionar um membro que já faz parte do projeto"""
    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id
        self.message = f"Usuário {user_id} já é membro do projeto {project_id}."
        super().__init__(self.message)


class InvalidTaskStateError(GestaoProjetosException):
    """Exceção lançada quando é tentada uma transição de estado inválida para uma tarefa"""
    def __init__(self, current_state, new_state):
        self.current_state = current_state
        self.new_state = new_state
        self.message = f"Transição de estado inválida: de '{current_state}' para '{new_state}'."
        super().__init__(self.message) 