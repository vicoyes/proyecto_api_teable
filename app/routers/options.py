from fastapi import APIRouter
from app.constants import (
    TASK_PRIORITIES, TASK_STATUSES, TASK_TYPES,
    TEAM_MEMBER_TYPES, TEAM_MEMBER_STATUSES,
    PROJECT_TYPES, PROJECT_STATUSES, PROJECT_PRIORITIES
)

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
