from fastapi import HTTPException
from app.clients.teable import TeableClient
from app.config import settings
from app.utils.mapping import map_project_record
from app.schemas.projects import ProjectCreate
from datetime import datetime


from app.utils.cache import project_cache

PROJECT_NAME_FIELD_ID = "fldsn21iQ3qa5pd1Wce"


class ProjectService:
    def __init__(self) -> None:
        self.client = TeableClient()
        self.table_id = settings.teable_table_projects

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

    async def create_project(self, project_data: ProjectCreate):
        fields = project_data.model_dump(exclude_unset=True)
        # Convert datetime to string if needed
        for key, value in fields.items():
            if isinstance(value, datetime):
                fields[key] = value.isoformat()
        
        try:
            # Proper Inverse Mapping for Teable fields
            inverse_map = {
                "nombre_proyecto": "Nombre_Proyecto",
                "descripcion": "Descripcion",
                "estado_proyecto": "Estado_Proyecto",
                "prioridad": "Prioridad",
                "fecha_inicio": "Fecha_Inicio",
                "fecha_fin": "Fecha_Fin",
                "presupuesto_estimado": "Presupuesto_Estimado",
                "tipo_proyecto": "Tipo_Proyecto",
                "notas_internas": "Notas_Internas"
            }
            
            teable_fields = {}
            for k, v in fields.items():
                if k in inverse_map and v is not None:
                    teable_fields[inverse_map[k]] = v
            
            if "nombre_proyecto" not in fields:
               teable_fields["Nombre_Proyecto"] = project_data.nombre_proyecto
                
            response = await self.client.create_record(self.table_id, {"fields": teable_fields})
            # invalidate cache
            project_cache._cache.clear()
            return map_project_record(response)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creando proyecto: {str(e)}")

    async def get_project_by_name(self, name: str):
        return await self.client.get_record_by_name(
            self.table_id,
            PROJECT_NAME_FIELD_ID,
            name,
        )
