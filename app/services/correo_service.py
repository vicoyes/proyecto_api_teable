import httpx
from fastapi import HTTPException, status

from app.clients.teable import TeableClient
from app.config import settings
from app.utils.mapping import map_correo_record
from app.schemas.correos import CorreoUpdate

# Field IDs de la tabla correos_electronicos (para filter/orderBy en Teable)
FLD_FROM_EMAIL = "fldxvpeSMYBnp6oztfp"
FLD_TO_EMAIL = "fldALpB0mAyL1u1PS9O"
FLD_TIPO = "fldJNY0SvDFpBnKvFqG"  # Single select: recibido, enviado


class CorreoService:
    def __init__(self) -> None:
        self.client = TeableClient()
        self.table_id = (settings.teable_table_correos or "").strip()

    def _require_table_id(self) -> None:
        if not self.table_id:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Correos no configurados: defina TEABLE_TABLE_CORREOS en el entorno (ej. .env o Portainer).",
            )

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
    def _map_to_teable(fields: dict) -> dict:
        """Mapea los nombres del payload a los nombres de campo en Teable.

        En esta tabla coinciden 1:1, pero dejamos el método por si en el futuro
        hubiera diferencias de naming.
        """
        return {k: v for k, v in fields.items() if v is not None}

    async def list_correos(
        self,
        skip: int = 0,
        take: int = 100,
        email: str | None = None,
        to_email: str | None = None,
        tipo: str | None = None,
    ):
        self._require_table_id()
        filter_obj = None
        if email or to_email or tipo:
            filter_set = []
            if email:
                filter_set.append({"fieldId": FLD_FROM_EMAIL, "operator": "is", "value": email})
            if to_email:
                filter_set.append({"fieldId": FLD_TO_EMAIL, "operator": "is", "value": to_email})
            if tipo:
                filter_set.append({"fieldId": FLD_TIPO, "operator": "is", "value": tipo})
            filter_obj = {"conjunction": "and", "filterSet": filter_set}

        data = await self.client.list_records(
            self.table_id,
            skip=skip,
            take=min(take, 1000),
            filter_obj=filter_obj,
        )
        records = data.get("records", [])
        items = [map_correo_record(r) for r in records]
        return {"total": len(items), "items": items}

    async def get_correo(self, record_id: str):
        self._require_table_id()
        try:
            record = await self.client.get_record(self.table_id, record_id)
            return map_correo_record(record)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Correo no encontrado") from exc
            detail = self._build_teable_error_detail(exc, "Error obteniendo correo")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def update_correo(self, record_id: str, payload: CorreoUpdate):
        self._require_table_id()
        fields = payload.model_dump(exclude_unset=True)

        if not fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos para actualizar",
            )

        teable_fields = self._map_to_teable(fields)

        try:
            response = await self.client.update_record(self.table_id, record_id, teable_fields)
            return map_correo_record(response)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Correo no encontrado") from exc
            detail = self._build_teable_error_detail(exc, "Error actualizando correo")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
