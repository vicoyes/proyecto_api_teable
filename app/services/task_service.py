from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, status

from app.clients.teable import TeableClient
from app.config import settings
from app.schemas.tasks import TaskCreate, TaskUpdate
from app.services.project_service import ProjectService
from app.services.team_service import TeamService
from app.utils.mapping import map_task_record


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
        """Lista tareas con filtro opcional por estado.
        
        Nota: El filtro de Teable no funciona correctamente,
        por lo que se filtra localmente cuando se especifica estado.
        """
        # Obtener más registros si hay filtro, porque filtraremos localmente
        fetch_take = take * 5 if estado else take
        
        data = await self.client.list_records(
            self.table_id,
            skip=0 if estado else skip,
            take=fetch_take,
        )
        
        records = data.get("records", [])
        
        # Filtrar localmente si hay estado
        if estado:
            records = [
                r for r in records 
                if r.get("fields", {}).get("estado_tarea") == estado
            ]
            # Aplicar paginación manualmente
            records = records[skip:skip + take]
        
        items = [map_task_record(record) for record in records]
        return {"total": len(items), "items": items}

    async def create_task(self, payload: TaskCreate):
        fields = payload.model_dump(exclude_none=True)

        if payload.responsable:
            member = await self.team_service.get_member_by_name(payload.responsable)
            if not member:
                raise HTTPException(status_code=404, detail="Responsable no encontrado")
            fields["responsable"] = self._build_link_field(member)

        project_link: dict[str, str] | None = None
        if payload.proyecto:
            project = await self.project_service.get_project_by_id_or_name(payload.proyecto)
            if not project:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")
            project_link = self._build_link_field(project)

        # El schema usa "proyecto"; Teable espera "Proyecto" o el field id fld… (no enviar la clave en minúsculas)
        fields.pop("proyecto", None)
        proyecto_fld = (settings.teable_field_tasks_proyecto_fld or "").strip()
        if project_link and not proyecto_fld:
            fields[settings.teable_field_tasks_proyecto] = project_link

        teable_fields = {k: v for k, v in fields.items() if v is not None}

        try:
            data = await self.client.create_record(self.table_id, teable_fields)
            record = data.get("records", [])[0]
            rid = record["id"]
            if project_link and proyecto_fld:
                await self.client.update_record(
                    self.table_id,
                    rid,
                    {proyecto_fld: project_link},
                    field_key_type="id",
                )
                record = await self.client.get_record(self.table_id, rid)
            return map_task_record(record)
        except httpx.HTTPStatusError as exc:
            detail = self._build_teable_error_detail(exc, "Error creando tarea")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc

    async def update_task(self, task_id: str, payload: TaskUpdate):
        fields = payload.model_dump(exclude_none=True)

        if payload.responsable:
            member = await self.team_service.get_member_by_name(payload.responsable)
            if not member:
                raise HTTPException(status_code=404, detail="Responsable no encontrado")
            fields["responsable"] = self._build_link_field(member)

        project_link: dict[str, str] | None = None
        if payload.proyecto:
            project = await self.project_service.get_project_by_id_or_name(payload.proyecto)
            if not project:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")
            project_link = self._build_link_field(project)

        fields.pop("proyecto", None)
        proyecto_fld = (settings.teable_field_tasks_proyecto_fld or "").strip()
        if project_link and not proyecto_fld:
            fields[settings.teable_field_tasks_proyecto] = project_link

        if payload.estado_tarea == "EN_PROGRESO" and "fecha_inicio" not in fields:
            fields["fecha_inicio"] = datetime.now(timezone.utc).isoformat()

        if payload.estado_tarea in {"COMPLETADA", "CANCELADA"} and "fecha_cierre" not in fields:
            fields["fecha_cierre"] = datetime.now(timezone.utc).isoformat()

        teable_fields = {k: v for k, v in fields.items() if v is not None}

        if not teable_fields and not (project_link and proyecto_fld):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos para actualizar",
            )

        try:
            data = None
            if teable_fields:
                data = await self.client.update_record(self.table_id, task_id, teable_fields)
            if project_link and proyecto_fld:
                await self.client.update_record(
                    self.table_id,
                    task_id,
                    {proyecto_fld: project_link},
                    field_key_type="id",
                )
                data = await self.client.get_record(self.table_id, task_id)
            elif data is None:
                data = await self.client.get_record(self.table_id, task_id)
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
        """Obtiene tareas asignadas a un miembro.
        
        Nota: El filtro de Teable no funciona correctamente,
        por lo que se obtienen todas las tareas y se filtra localmente.
        """
        member = await self.team_service.get_member_by_name(member_name)
        if not member:
            raise HTTPException(status_code=404, detail="Miembro no encontrado")

        member_id = member["id"]

        # Obtener todas las tareas y filtrar localmente
        data = await self.client.list_records(self.table_id, take=500)
        
        filtered_records = []
        for record in data.get("records", []):
            fields = record.get("fields", {})
            responsable = fields.get("responsable")
            
            # responsable es un objeto {"id": "recXXX", "title": "Nombre"}
            if isinstance(responsable, dict) and responsable.get("id") == member_id:
                # Filtrar por estado si se especifica
                if estado is None or fields.get("estado_tarea") == estado:
                    filtered_records.append(record)

        items = [map_task_record(record) for record in filtered_records]
        return {
            "responsable": member_name,
            "estado": estado,
            "total": len(items),
            "items": items,
        }

    async def get_member_task_summary(self, member_name: str):
        """Obtiene resumen de tareas por estado para un miembro.
        
        Nota: El filtro de Teable no funciona correctamente,
        por lo que se obtienen todas las tareas y se filtra localmente.
        """
        member = await self.team_service.get_member_by_name(member_name)
        if not member:
            raise HTTPException(status_code=404, detail="Miembro no encontrado")

        member_id = member["id"]

        # Obtener todas las tareas y filtrar localmente
        data = await self.client.list_records(self.table_id, take=500)

        counts: dict[str, int] = {}
        for record in data.get("records", []):
            fields = record.get("fields", {})
            responsable = fields.get("responsable")
            
            # responsable es un objeto {"id": "recXXX", "title": "Nombre"}
            if isinstance(responsable, dict) and responsable.get("id") == member_id:
                estado = fields.get("estado_tarea", "SIN_ESTADO")
                counts[estado] = counts.get(estado, 0) + 1

        return {
            "responsable": member_name,
            "counts": counts,
        }

    async def get_tasks_by_project(self, project_id: str, estado: str | None = None):
        """Obtiene tareas asociadas a un proyecto (filter local por campo relacional Proyecto)."""
        # Cargamos un número razonable de tareas y filtramos localmente,
        # siguiendo el patrón usado en otros métodos.
        data = await self.client.list_records(self.table_id, take=500)

        filtered_records = []
        for record in data.get("records", []):
            fields = record.get("fields", {})
            proyecto = fields.get("Proyecto")

            # Proyecto es un objeto {"id": "recXXX", "title": "..."} o None
            if isinstance(proyecto, dict) and proyecto.get("id") == project_id:
                if estado is None or fields.get("estado_tarea") == estado:
                    filtered_records.append(record)

        items = [map_task_record(record) for record in filtered_records]
        return {
            "proyecto_id": project_id,
            "estado": estado,
            "total": len(items),
            "items": items,
        }

    async def get_tasks_by_client(self, cliente_id: str, estado: str | None = None):
        """Obtiene tareas asociadas a todos los proyectos de un cliente."""
        # 1) Obtener todos los proyectos de ese cliente
        from app.services.project_service import ProjectService  # import local para evitar ciclos

        project_service = ProjectService()
        proyectos_data = await project_service.list_projects_by_client(cliente_id)
        project_ids = [item.id for item in proyectos_data["items"]]

        if not project_ids:
            return {
                "cliente_id": cliente_id,
                "estado": estado,
                "total": 0,
                "items": [],
            }

        # 2) Cargar tareas y filtrar localmente por Proyecto.id en project_ids
        data = await self.client.list_records(self.table_id, take=500)

        filtered_records = []
        project_ids_set = set(project_ids)

        for record in data.get("records", []):
            fields = record.get("fields", {})
            proyecto = fields.get("Proyecto")

            if isinstance(proyecto, dict) and proyecto.get("id") in project_ids_set:
                if estado is None or fields.get("estado_tarea") == estado:
                    filtered_records.append(record)

        items = [map_task_record(record) for record in filtered_records]
        return {
            "cliente_id": cliente_id,
            "estado": estado,
            "total": len(items),
            "items": items,
        }
