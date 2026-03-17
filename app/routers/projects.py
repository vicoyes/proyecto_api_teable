from fastapi import APIRouter, Query, status

from app.schemas.projects import ProjectListResponse, ProjectResponse, ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = Query(0, ge=0), take: int = Query(50, ge=1, le=100)
):
    service = ProjectService()
    return await service.list_projects(skip=skip, take=take)


@router.get("/by-client/{cliente_id}", response_model=ProjectListResponse)
async def list_projects_by_client(
    cliente_id: str,
    skip: int = Query(0, ge=0),
    take: int = Query(50, ge=1, le=100),
):
    """Lista proyectos vinculados a un cliente concreto."""
    service = ProjectService()
    return await service.list_projects_by_client(cliente_id, skip=skip, take=take)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate):
    service = ProjectService()
    return await service.create_project(payload)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, payload: ProjectUpdate):
    service = ProjectService()
    return await service.update_project(project_id, payload)
