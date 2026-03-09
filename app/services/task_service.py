from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, status

from app.clients.teable import TeableClient
from app.config import settings
from app.schemas.tasks import TaskCreate, TaskUpdate
from app.services.project_service import ProjectService
from app.services.team_service import TeamService
from app.utils.mapping import map_task_record


TASK_STATUS_FIELD_ID = "fldPjj7OY4dBTAjTab4"
TASK_RESPONSABLE_FIELD_ID = "fldo2yTWNciX7xYsh3u"


class TaskService:
    def __init__(self) -> None:
        self.client = TeableClient()
        self.table_id = settings.teable_table_tasks
        self.team_service = TeamService()
        self.project_service = ProjectService()

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
    def _build_link_field(record: dict) -> dict[str, str]:
        return {"id": record["id"]}

    async def list_tasks(self, skip: int = 0, take: int = 50, estado: str | None = None):
        filter_obj = None
        if estado:
            filter_obj = {
                "conjunction": "and",
                "filterSet": [
                    {"fieldId": TASK_STATUS_FIELD_ID, "operator": "is", "value": estado},
                ],
            }

        data = await self.client.list_records(
            self.table_id,
            skip=skip,
            take=take,
            filter_obj=filter_obj,
        )
        items = [map_task_record(record) for record in data.get("records", [])]
        return {"total": len(items), "items": items}

    async def create_task(self, payload: TaskCreate):
        fields = payload.model_dump(exclude_none=True)

        if payload.responsable:
            member = await self.team_service.get_member_by_name(payload.responsable)
            if not member:
                raise HTTPException(status_code=404, detail="Responsable no encontrado")
            fields["responsable"] = self._build_link_field(member)

        if payload.proyecto:
            project = await self.project_service.get_project_by_name(payload.proyecto)
            if not project:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")
            fields["proyecto"] = self._build_link_field(project)

        teable_fields = {k: v for k, v in fields.items() if v is not None}

        try:
            data = await self.client.create_record(self.table_id, teable_fields)
            record = data.get("records", [])[0]
            return map_task_record(record)
        except httpx.HTTPStatusError as exc:
            detail = self._build_teable_error_detail(exc, "Error creando tarea")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def update_task(self, task_id: str, payload: TaskUpdate):
        fields = payload.model_dump(exclude_none=True)

        if not fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos para actualizar",
            )

        if payload.responsable:
            member = await self.team_service.get_member_by_name(payload.responsable)
            if not member:
                raise HTTPException(status_code=404, detail="Responsable no encontrado")
            fields["responsable"] = self._build_link_field(member)

        if payload.proyecto:
            project = await self.project_service.get_project_by_name(payload.proyecto)
            if not project:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")
            fields["proyecto"] = self._build_link_field(project)

        if payload.estado_tarea == "EN_PROGRESO" and "fecha_inicio" not in fields:
            fields["fecha_inicio"] = datetime.now(timezone.utc).isoformat()

        if payload.estado_tarea in {"COMPLETADA", "CANCELADA"} and "fecha_cierre" not in fields:
            fields["fecha_cierre"] = datetime.now(timezone.utc).isoformat()

        teable_fields = {k: v for k, v in fields.items() if v is not None}

        try:
            data = await self.client.update_record(self.table_id, task_id, teable_fields)
            return map_task_record(data)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Tarea no encontrada") from exc

            detail = self._build_teable_error_detail(exc, "Error actualizando tarea")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def get_task(self, task_id: str):
        try:
            data = await self.client.get_record(self.table_id, task_id)
            return map_task_record(data)
        except Exception:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")

    async def delete_task(self, task_id: str):
        return await self.client.delete_record(self.table_id, task_id)

    async def get_tasks_by_member(self, member_name: str, estado: str | None = None):
        member = await self.team_service.get_member_by_name(member_name)
        if not member:
            raise HTTPException(status_code=404, detail="Miembro no encontrado")

        filter_set = [
            {
                "fieldId": TASK_RESPONSABLE_FIELD_ID,
                "operator": "contains",
                "value": member["id"],
            }
        ]

        if estado:
            filter_set.append(
                {
                    "fieldId": TASK_STATUS_FIELD_ID,
                    "operator": "is",
                    "value": estado,
                }
            )

        filter_obj = {
            "conjunction": "and",
            "filterSet": filter_set,
        }

        data = await self.client.list_records(
            self.table_id,
            take=100,
            filter_obj=filter_obj,
        )
        items = [map_task_record(record) for record in data.get("records", [])]
        return {
            "responsable": member_name,
            "estado": estado,
            "total": len(items),
            "items": items,
        }

    async def get_member_task_summary(self, member_name: str):
        member = await self.team_service.get_member_by_name(member_name)
        if not member:
            raise HTTPException(status_code=404, detail="Miembro no encontrado")

        filter_obj = {
            "conjunction": "and",
            "filterSet": [
                {
                    "fieldId": TASK_RESPONSABLE_FIELD_ID,
                    "operator": "contains",
                    "value": member["id"],
                }
            ],
        }

        data = await self.client.list_records(
            self.table_id,
            take=200,
            filter_obj=filter_obj,
        )

        counts: dict[str, int] = {}
        for record in data.get("records", []):
            estado = record.get("fields", {}).get("estado_tarea", "SIN_ESTADO")
            counts[estado] = counts.get(estado, 0) + 1

        return {
            "responsable": member_name,
            "counts": counts,
        }
