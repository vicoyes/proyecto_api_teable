from fastapi import APIRouter, Query, status

from app.schemas.clientes import ClienteListResponse, ClienteResponse, ClienteCreate, ClienteUpdate
from app.schemas.common import ApiMessage
from app.services.cliente_service import ClienteService


router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=ClienteListResponse)
async def list_clientes(
    skip: int = Query(0, ge=0), take: int = Query(50, ge=1, le=100)
):
    service = ClienteService()
    return await service.list_clientes(skip=skip, take=take)

@router.get("/{cliente_id}", response_model=ClienteResponse)
async def get_cliente(cliente_id: str):
    service = ClienteService()
    return await service.get_cliente(cliente_id)

@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente(payload: ClienteCreate):
    service = ClienteService()
    return await service.create_cliente(payload)

@router.patch("/{cliente_id}", response_model=ClienteResponse)
async def update_cliente(cliente_id: str, payload: ClienteUpdate):
    service = ClienteService()
    return await service.update_cliente(cliente_id, payload)

@router.delete("/{cliente_id}", response_model=ApiMessage)
async def delete_cliente(cliente_id: str):
    service = ClienteService()
    return await service.delete_cliente(cliente_id)
