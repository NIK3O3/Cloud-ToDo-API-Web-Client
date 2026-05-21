import uuid
from datetime import date

import pytest
from app.core.errors import AppError
from app.domain.entities import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskPatch, TaskReplace


def test_create_task_with_defaults(task_service):
    task = task_service.create_task(TaskCreate(title="Write docs"))

    assert task.title == "Write docs"
    assert task.status == TaskStatus.NEW
    assert task.priority == TaskPriority.MEDIUM


def test_list_tasks_filters_by_status(task_service):
    task_service.create_task(TaskCreate(title="Task one", status=TaskStatus.NEW))
    task_service.create_task(TaskCreate(title="Task two", status=TaskStatus.DONE))

    items, total = task_service.list_tasks(status=TaskStatus.DONE, priority=None, limit=20, offset=0)

    assert total == 1
    assert items[0].status == TaskStatus.DONE


def test_list_tasks_filters_by_priority(task_service):
    task_service.create_task(TaskCreate(title="Low priority", priority=TaskPriority.LOW))
    task_service.create_task(TaskCreate(title="High priority", priority=TaskPriority.HIGH))

    items, total = task_service.list_tasks(status=None, priority=TaskPriority.HIGH, limit=20, offset=0)

    assert total == 1
    assert items[0].priority == TaskPriority.HIGH


def test_get_task_missing_raises_404(task_service):
    with pytest.raises(AppError) as exc:
        task_service.get_task(uuid.uuid4())

    assert exc.value.status_code == 404
    assert exc.value.code == "TASK_NOT_FOUND"


def test_replace_task_updates_all_editable_fields(task_service):
    created = task_service.create_task(TaskCreate(title="Old title"))

    replaced = task_service.replace_task(
        created.id,
        TaskReplace(
            title="New title",
            description="New description",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            dueDate=date(2026, 6, 1),
        ),
    )

    assert replaced.title == "New title"
    assert replaced.description == "New description"
    assert replaced.status == TaskStatus.IN_PROGRESS
    assert replaced.priority == TaskPriority.HIGH
    assert replaced.due_date == date(2026, 6, 1)


def test_patch_task_updates_status_and_priority(task_service):
    created = task_service.create_task(TaskCreate(title="Patch me"))

    patched = task_service.patch_task(
        created.id,
        TaskPatch(status=TaskStatus.DONE, priority=TaskPriority.LOW),
    )

    assert patched.status == TaskStatus.DONE
    assert patched.priority == TaskPriority.LOW


def test_delete_task_removes_task(task_service):
    created = task_service.create_task(TaskCreate(title="Delete me"))

    task_service.delete_task(created.id)

    with pytest.raises(AppError):
        task_service.get_task(created.id)
