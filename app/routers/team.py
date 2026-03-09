from fastapi import APIRouter, Query

from app.schemas.team import TeamListResponse
from app.services.team_service import TeamService

router = APIRouter(prefix="/team", tags=["team"])


@router.get("", response_model=TeamListResponse)
async def list_team(skip: int = Query(0, ge=0), take: int = Query(50, ge=1, le=100)):
    service = TeamService()
    return await service.list_members(skip=skip, take=take)
