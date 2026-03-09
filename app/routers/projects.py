from fastapi import APIRouter, Query

from app.schemas.projects import ProjectListResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
async def list_projects(skip: int = Query(0, ge=0), take: int = Query(50, ge=1, le=100)):
    service = ProjectService()
    return await service.list_projects(skip=skip, take=take)
