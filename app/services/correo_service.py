import httpx
from fastapi import HTTPException, status

from app.clients.teable import TeableClient
from app.config import settings
from app.utils.mapping import map_correo_record

# Field IDs de la tabla correos_electronicos (para filter/orderBy en Teable)
FLD_FROM_EMAIL = "fldxvpeSMYBnp6oztfp"
FLD_TO_EMAIL = "fldALpB0mAyL1u1PS9O"


class CorreoService:
    def __init__(self) -> None:
        self.client = TeableClient()
        self.table_id = settings.teable_table_correos

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

    async def list_correos(
        self,
        skip: int = 0,
        take: int = 100,
        email: str | None = None,
        to_email: str | None = None,
    ):
        filter_obj = None
        if email or to_email:
            filter_set = []
            if email:
                filter_set.append({"fieldId": FLD_FROM_EMAIL, "operator": "is", "value": email})
            if to_email:
                filter_set.append({"fieldId": FLD_TO_EMAIL, "operator": "is", "value": to_email})
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
        try:
            record = await self.client.get_record(self.table_id, record_id)
            return map_correo_record(record)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Correo no encontrado") from exc
            detail = self._build_teable_error_detail(exc, "Error obteniendo correo")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
