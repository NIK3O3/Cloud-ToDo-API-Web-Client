from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.domain.entities import TaskPriority, TaskStatus
from app.models.task import TaskModel
from app.schemas.task import TaskCreate, TaskPatch, TaskReplace


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: TaskCreate) -> TaskModel:
        task = TaskModel(
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            due_date=data.due_date,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list(
        self,
        *,
        status: TaskStatus | None,
        priority: TaskPriority | None,
        limit: int,
        offset: int,
    ) -> tuple[list[TaskModel], int]:
        base = self._filtered_query(status=status, priority=priority)
        total = self.db.scalar(select(func.count()).select_from(base.subquery())) or 0
        items = self.db.scalars(base.order_by(TaskModel.created_at.desc()).limit(limit).offset(offset)).all()
        return list(items), total

    def get(self, task_id: UUID) -> TaskModel | None:
        return self.db.get(TaskModel, task_id)

    def replace(self, task: TaskModel, data: TaskReplace) -> TaskModel:
        task.title = data.title
        task.description = data.description
        task.status = data.status
        task.priority = data.priority
        task.due_date = data.due_date
        self.db.commit()
        self.db.refresh(task)
        return task

    def patch(self, task: TaskModel, data: TaskPatch) -> TaskModel:
        if data.status is not None:
            task.status = data.status
        if data.priority is not None:
            task.priority = data.priority
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: TaskModel) -> None:
        self.db.delete(task)
        self.db.commit()

    @staticmethod
    def _filtered_query(
        *,
        status: TaskStatus | None,
        priority: TaskPriority | None,
    ) -> Select[tuple[TaskModel]]:
        query = select(TaskModel)
        if status is not None:
            query = query.where(TaskModel.status == status)
        if priority is not None:
            query = query.where(TaskModel.priority == priority)
        return query
