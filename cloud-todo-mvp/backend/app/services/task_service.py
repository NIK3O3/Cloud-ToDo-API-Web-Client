from uuid import UUID

from app.core.errors import AppError
from app.domain.entities import TaskPriority, TaskStatus
from app.models.task import TaskModel
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskPatch, TaskReplace


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def create_task(self, data: TaskCreate) -> TaskModel:
        return self.repository.create(data)

    def list_tasks(
        self,
        *,
        status: TaskStatus | None,
        priority: TaskPriority | None,
        limit: int,
        offset: int,
    ) -> tuple[list[TaskModel], int]:
        return self.repository.list(status=status, priority=priority, limit=limit, offset=offset)

    def get_task(self, task_id: UUID) -> TaskModel:
        task = self.repository.get(task_id)
        if task is None:
            raise AppError(code="TASK_NOT_FOUND", message="Task not found", status_code=404)
        return task

    def replace_task(self, task_id: UUID, data: TaskReplace) -> TaskModel:
        task = self.get_task(task_id)
        return self.repository.replace(task, data)

    def patch_task(self, task_id: UUID, data: TaskPatch) -> TaskModel:
        task = self.get_task(task_id)
        return self.repository.patch(task, data)

    def delete_task(self, task_id: UUID) -> None:
        task = self.get_task(task_id)
        self.repository.delete(task)
