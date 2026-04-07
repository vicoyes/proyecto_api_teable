import httpx
from fastapi import HTTPException, status

from app.clients.teable import TeableClient
from app.config import settings
from app.schemas.tickets import TicketCreate, TicketUpdate
from app.utils.mapping import map_ticket_record


class TicketService:
    def __init__(self) -> None:
        self.client = TeableClient()
        self.table_id = settings.teable_table_tickets

    @staticmethod
    def _build_teable_error_detail(exc: httpx.HTTPStatusError, default_message: str) -> str:
        try:
            payload = exc.response.json()
        except ValueError:
            text = exc.response.text.strip()
            return text or default_message

        if isinstance(payload, dict):
            for key in ("message", "detail", "error"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value

        return default_message

    @staticmethod
    def _payload_to_teable_fields(data: dict) -> dict:
        """Mapea el schema de la API al nombre de campo en Teable (fieldKeyType=name)."""
        out: dict = {}
        for k, v in data.items():
            if v is None:
                continue
            if k == "numero_ticket":
                out["id"] = v
            elif k == "estado":
                out["Estado"] = v
            else:
                out[k] = v
        return out

    async def list_tickets(
        self,
        skip: int = 0,
        take: int = 50,
        search: str | None = None,
    ):
        data = await self.client.list_records(
            self.table_id,
            skip=skip,
            take=take,
            search=search,
        )
        items = [map_ticket_record(r) for r in data.get("records", [])]
        return {"total": len(items), "items": items}

    async def get_ticket(self, record_id: str):
        try:
            record = await self.client.get_record(self.table_id, record_id)
            return map_ticket_record(record)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Ticket no encontrado") from exc
            detail = self._build_teable_error_detail(exc, "Error obteniendo ticket")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def create_ticket(self, payload: TicketCreate):
        fields = payload.model_dump(exclude_unset=True)
        teable_fields = self._payload_to_teable_fields(fields)
        try:
            response = await self.client.create_record(self.table_id, teable_fields)
            return map_ticket_record(response.get("records", [])[0])
        except httpx.HTTPStatusError as exc:
            detail = self._build_teable_error_detail(exc, "Error creando ticket")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def update_ticket(self, record_id: str, payload: TicketUpdate):
        fields = payload.model_dump(exclude_unset=True)
        if not fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos para actualizar",
            )
        teable_fields = self._payload_to_teable_fields(fields)
        try:
            response = await self.client.update_record(self.table_id, record_id, teable_fields)
            return map_ticket_record(response)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Ticket no encontrado") from exc
            detail = self._build_teable_error_detail(exc, "Error actualizando ticket")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def delete_ticket(self, record_id: str):
        try:
            await self.client.delete_record(self.table_id, record_id)
            return {"message": "Ticket eliminado correctamente"}
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Ticket no encontrado") from exc
            detail = self._build_teable_error_detail(exc, "Error eliminando ticket")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
