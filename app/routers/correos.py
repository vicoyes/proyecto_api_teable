from fastapi import APIRouter, Query

from app.schemas.correos import CorreoListResponse, CorreoResponse
from app.services.correo_service import CorreoService


router = APIRouter(prefix="/correos-electronicos", tags=["correos-electronicos"])


@router.get("", response_model=CorreoListResponse)
async def list_correos(
    skip: int = Query(0, ge=0),
    take: int = Query(100, ge=1, le=1000),
    email: str | None = Query(None, description="Filtrar por email del remitente (from_email)"),
    to_email: str | None = Query(None, description="Filtrar por email del destinatario (to_email)"),
):
    """Lista correos electrónicos. Opcionalmente filtra por remitente (email) o destinatario (to_email)."""
    service = CorreoService()
    return await service.list_correos(skip=skip, take=take, email=email, to_email=to_email)


@router.get("/{record_id}", response_model=CorreoResponse)
async def get_correo(record_id: str):
    """Obtiene un correo electrónico por su ID de registro."""
    service = CorreoService()
    return await service.get_correo(record_id)
