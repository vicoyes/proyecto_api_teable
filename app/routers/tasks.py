from fastapi import APIRouter, Query, status

from app.schemas.common import ApiMessage
from app.schemas.tasks import MemberTaskSummary, TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    skip: int = Query(0, ge=0),
    take: int = Query(50, ge=1, le=100),
    estado: str | None = Query(None),
):
    service = TaskService()
    return await service.list_tasks(skip=skip, take=take, estado=estado)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate):
    service = TaskService()
    return await service.create_task(payload)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    service = TaskService()
    from fastapi import HTTPException
    try:
        return await service.get_task(task_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, payload: TaskUpdate):
    service = TaskService()
    return await service.update_task(task_id, payload)


@router.post("/{task_id}/start", response_model=TaskResponse)
async def start_task(task_id: str):
    service = TaskService()
    return await service.update_task(task_id, TaskUpdate(estado_tarea="EN_PROGRESO"))


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: str):
    service = TaskService()
    return await service.update_task(task_id, TaskUpdate(estado_tarea="COMPLETADA"))


@router.post("/{task_id}/block", response_model=TaskResponse)
async def block_task(task_id: str):
    service = TaskService()
    return await service.update_task(task_id, TaskUpdate(estado_tarea="BLOQUEADA"))


@router.delete("/{task_id}", response_model=ApiMessage)
async def delete_task(task_id: str):
    service = TaskService()
    await service.delete_task(task_id)
    return {"message": "Tarea eliminada correctamente"}


@router.get("/by-member/{member_name}")
async def get_tasks_by_member(
    member_name: str,
    estado: str | None = Query(None),
):
    service = TaskService()
    return await service.get_tasks_by_member(member_name, estado=estado)


@router.get("/by-member/{member_name}/summary", response_model=MemberTaskSummary)
async def get_member_task_summary(member_name: str):
    service = TaskService()
    return await service.get_member_task_summary(member_name)


@router.get("/by-project/{project_id}")
async def get_tasks_by_project(
    project_id: str,
    estado: str | None = Query(None),
):
    """Lista tareas asociadas a un proyecto concreto."""
    service = TaskService()
    return await service.get_tasks_by_project(project_id, estado=estado)


@router.get("/by-client/{cliente_id}")
async def get_tasks_by_client(
    cliente_id: str,
    estado: str | None = Query(None),
):
    """Lista tareas asociadas a todos los proyectos de un cliente."""
    service = TaskService()
    return await service.get_tasks_by_client(cliente_id, estado=estado)
