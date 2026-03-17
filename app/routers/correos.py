from typing import Literal

from fastapi import APIRouter, Query

from app.schemas.correos import CorreoListResponse, CorreoResponse, CorreoUpdate
from app.services.correo_service import CorreoService


router = APIRouter(prefix="/correos-electronicos", tags=["correos-electronicos"])


@router.get("", response_model=CorreoListResponse)
async def list_correos(
    skip: int = Query(0, ge=0),
    take: int = Query(100, ge=1, le=1000),
    email: str | None = Query(None, description="Filtrar por email del remitente (from_email)"),
    to_email: str | None = Query(None, description="Filtrar por email del destinatario (to_email)"),
    tipo: Literal["enviado", "recibido"] | None = Query(
        None,
        description="Filtrar por tipo de correo: enviado o recibido",
    ),
):
    """Lista correos electrónicos. Filtros opcionales: email, to_email, tipo (enviado|recibido)."""
    service = CorreoService()
    return await service.list_correos(skip=skip, take=take, email=email, to_email=to_email, tipo=tipo)


@router.get("/{record_id}", response_model=CorreoResponse)
async def get_correo(record_id: str):
    """Obtiene un correo electrónico por su ID de registro."""
    service = CorreoService()
    return await service.get_correo(record_id)


@router.patch("/{record_id}", response_model=CorreoResponse)
async def update_correo(record_id: str, payload: CorreoUpdate):
    """Actualiza campos de un correo existente. No crea registros nuevos."""
    service = CorreoService()
    return await service.update_correo(record_id, payload)
