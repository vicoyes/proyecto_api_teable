from fastapi import APIRouter, Query, status

from app.schemas.common import ApiMessage
from app.schemas.tickets import TicketCreate, TicketListResponse, TicketResponse, TicketUpdate
from app.services.ticket_service import TicketService


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    skip: int = Query(0, ge=0),
    take: int = Query(50, ge=1, le=1000),
    search: str | None = Query(None, description="Búsqueda en todos los campos (Teable)"),
):
    service = TicketService()
    return await service.list_tickets(skip=skip, take=take, search=search)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str):
    service = TicketService()
    return await service.get_ticket(ticket_id)


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(payload: TicketCreate):
    service = TicketService()
    return await service.create_ticket(payload)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: str, payload: TicketUpdate):
    service = TicketService()
    return await service.update_ticket(ticket_id, payload)


@router.delete("/{ticket_id}", response_model=ApiMessage)
async def delete_ticket(ticket_id: str):
    service = TicketService()
    return await service.delete_ticket(ticket_id)
