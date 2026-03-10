from fastapi import APIRouter
from app.constants import (
    TASK_PRIORITIES, TASK_STATUSES, TASK_TYPES,
    TEAM_MEMBER_TYPES, TEAM_MEMBER_STATUSES,
    PROJECT_TYPES, PROJECT_STATUSES, PROJECT_PRIORITIES
)
from app.utils.cache import invalidate_all_caches, team_cache, project_cache

router = APIRouter(prefix="/options", tags=["options"])


@router.get("")
async def get_options():
    return {
        "tasks": {
            "priorities": TASK_PRIORITIES,
            "statuses": TASK_STATUSES,
            "types": TASK_TYPES,
        },
        "team": {
            "member_types": TEAM_MEMBER_TYPES,
            "statuses": TEAM_MEMBER_STATUSES,
        },
        "projects": {
            "types": PROJECT_TYPES,
            "statuses": PROJECT_STATUSES,
            "priorities": PROJECT_PRIORITIES,
        }
    }


@router.post("/cache/invalidate")
async def invalidate_cache():
    """Invalida el caché de miembros y proyectos.
    
    Útil después de agregar, modificar o eliminar miembros o proyectos en Teable.
    """
    invalidate_all_caches()
    return {"message": "Caché invalidado correctamente"}


@router.post("/cache/invalidate/team")
async def invalidate_team_cache():
    """Invalida solo el caché de miembros del equipo."""
    team_cache.clear()
    return {"message": "Caché de equipo invalidado"}


@router.post("/cache/invalidate/projects")
async def invalidate_projects_cache():
    """Invalida solo el caché de proyectos."""
    project_cache.clear()
    return {"message": "Caché de proyectos invalidado"}
