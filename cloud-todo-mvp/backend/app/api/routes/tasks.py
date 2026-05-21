from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_task_service
from app.core.security import require_api_key
from app.domain.entities import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskListResponse, TaskPatch, TaskReplace, TaskResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, service: TaskService = Depends(get_task_service)):
    return service.create_task(payload)


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: TaskService = Depends(get_task_service),
) -> TaskListResponse:
    items, total = service.list_tasks(status=status_filter, priority=priority, limit=limit, offset=offset)
    return TaskListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, service: TaskService = Depends(get_task_service)):
    return service.get_task(task_id)


@router.put("/{task_id}", response_model=TaskResponse)
def replace_task(task_id: UUID, payload: TaskReplace, service: TaskService = Depends(get_task_service)):
    return service.replace_task(task_id, payload)


@router.patch("/{task_id}", response_model=TaskResponse)
def patch_task(task_id: UUID, payload: TaskPatch, service: TaskService = Depends(get_task_service)):
    return service.patch_task(task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, service: TaskService = Depends(get_task_service)) -> Response:
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
