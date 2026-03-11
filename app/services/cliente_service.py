import httpx
from fastapi import HTTPException, status

from app.clients.teable import TeableClient
from app.config import settings
from app.utils.mapping import map_cliente_record
from app.schemas.clientes import ClienteCreate, ClienteUpdate


class ClienteService:
    def __init__(self) -> None:
        self.client = TeableClient()
        self.table_id = settings.teable_table_clientes

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

    def _map_to_teable(self, data: dict) -> dict:
        mapping = {
            "etiqueta": "Etiqueta",
            "nombre_del_cliente": "Nombre del Cliente",
            "email": "Email",
            "empresa": "Empresa",
            "numero_de_telefono": "Numero de telefono",
            "notas": "Notas"
        }
        return {mapping[k]: v for k, v in data.items() if k in mapping and v is not None}

    async def list_clientes(self, skip: int = 0, take: int = 50):
        data = await self.client.list_records(self.table_id, skip=skip, take=take)
        items = [map_cliente_record(record) for record in data.get("records", [])]
        return {"total": len(items), "items": items}

    async def get_cliente(self, record_id: str):
        try:
            record = await self.client.get_record(self.table_id, record_id)
            return map_cliente_record(record)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Cliente no encontrado") from exc
            detail = self._build_teable_error_detail(exc, "Error obteniendo cliente")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def create_cliente(self, cliente_data: ClienteCreate):
        fields = cliente_data.model_dump(exclude_unset=True)
        teable_fields = self._map_to_teable(fields)
        
        try:
            response = await self.client.create_record(self.table_id, teable_fields)
            return map_cliente_record(response.get("records", [])[0])
        except httpx.HTTPStatusError as exc:
            detail = self._build_teable_error_detail(exc, "Error creando cliente")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def update_cliente(self, record_id: str, cliente_data: ClienteUpdate):
        fields = cliente_data.model_dump(exclude_unset=True)

        if not fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos para actualizar",
            )
            
        teable_fields = self._map_to_teable(fields)
        
        try:
            response = await self.client.update_record(self.table_id, record_id, teable_fields)
            return map_cliente_record(response)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Cliente no encontrado") from exc

            detail = self._build_teable_error_detail(exc, "Error actualizando cliente")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def delete_cliente(self, record_id: str):
        try:
            await self.client.delete_record(self.table_id, record_id)
            return {"message": "Cliente eliminado correctamente"}
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Cliente no encontrado") from exc
            detail = self._build_teable_error_detail(exc, "Error eliminando cliente")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
