import re

import httpx
from fastapi import HTTPException, status
from app.clients.teable import TeableClient
from app.config import settings
from app.utils.mapping import map_project_record
from app.schemas.projects import ProjectCreate, ProjectUpdate
from datetime import datetime
from app.utils.cache import project_cache


class ProjectService:
    def __init__(self) -> None:
        self.client = TeableClient()
        self.table_id = settings.teable_table_projects

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

    async def list_projects(self, skip: int = 0, take: int = 50):
        cache_key = f"list_projects_{skip}_{take}"
        cached = project_cache.get(cache_key)
        if cached:
            return cached

        data = await self.client.list_records(self.table_id, skip=skip, take=take)
        items = [map_project_record(record) for record in data.get("records", [])]
        result = {"total": len(items), "items": items}
        project_cache.set(cache_key, result)
        return result

    async def list_projects_by_client(self, cliente_id: str, skip: int = 0, take: int = 100):
        """Lista proyectos vinculados a un cliente concreto (filter local por campo Cliente)."""
        # Reutilizamos la caché de proyectos para evitar golpear Teable en exceso.
        cache_key = "all_projects_for_client_search"
        cached = project_cache.get(cache_key)

        if cached:
            records = cached
        else:
            data = await self.client.list_records(self.table_id, take=500)
            records = data.get("records", [])
            project_cache.set(cache_key, records)

        filtered_records = []
        for record in records:
            fields = record.get("fields", {})
            cliente = fields.get("Cliente")
            # Cliente es un objeto {"id": "recXXX", "title": "..."} o None
            if isinstance(cliente, dict) and cliente.get("id") == cliente_id:
                filtered_records.append(record)

        # Aplicar paginación sobre el resultado filtrado
        paginated = filtered_records[skip:skip + take]
        items = [map_project_record(record) for record in paginated]
        return {"total": len(items), "items": items}

    async def create_project(self, project_data: ProjectCreate):
        fields = project_data.model_dump(exclude_unset=True)
        # Convert datetime to string if needed
        for key, value in fields.items():
            if isinstance(value, datetime):
                fields[key] = value.isoformat()
        
        try:
            # Send fields exactly matching the Pydantic schema snake_case as they correspond
            # exactly to the Teable column names we defined in mapping.py
            teable_fields = {k: v for k, v in fields.items() if v is not None}

            response = await self.client.create_record(self.table_id, teable_fields)
            # invalidate cache
            project_cache._cache.clear()
            return map_project_record(response.get("records", [])[0])
        except httpx.HTTPStatusError as exc:
            detail = self._build_teable_error_detail(exc, "Error creando proyecto")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def get_project_by_name(self, name: str):
        """Busca un proyecto por nombre exacto.
        
        Nota: El filtro de Teable no funciona correctamente,
        por lo que se obtienen todos los proyectos y se filtra localmente.
        """
        cache_key = "all_projects_for_search"
        cached = project_cache.get(cache_key)
        
        if cached:
            records = cached
        else:
            data = await self.client.list_records(self.table_id, take=100)
            records = data.get("records", [])
            project_cache.set(cache_key, records)
        
        # Filtrar localmente por nombre exacto
        for record in records:
            fields = record.get("fields", {})
            if fields.get("nombre_proyecto") == name:
                return record
        
        return None

    _TEABLE_RECORD_ID = re.compile(r"^rec[A-Za-z0-9]+$")

    async def get_project_by_id_or_name(self, value: str) -> dict | None:
        """Resuelve un proyecto por ID de registro Teable (`rec…`) o por `nombre_proyecto` exacto."""
        raw = value.strip()
        if not raw:
            return None

        if self._TEABLE_RECORD_ID.match(raw):
            try:
                return await self.client.get_record(self.table_id, raw)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                    return await self.get_project_by_name(raw)
                raise

        return await self.get_project_by_name(raw)

    async def update_project(self, project_id: str, project_data: ProjectUpdate):
        fields = project_data.model_dump(exclude_unset=True)

        if not fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos para actualizar",
            )

        # Convert datetime to string if needed
        for key, value in fields.items():
            if isinstance(value, datetime):
                fields[key] = value.isoformat()
        
        try:
            teable_fields = {k: v for k, v in fields.items() if v is not None}
            response = await self.client.update_record(self.table_id, project_id, teable_fields)
            # invalidate cache
            project_cache._cache.clear()
            return map_project_record(response)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado") from exc

            detail = self._build_teable_error_detail(exc, "Error actualizando proyecto")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
