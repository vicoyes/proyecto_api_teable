from fastapi import HTTPException
from app.clients.teable import TeableClient
from app.config import settings
from app.utils.mapping import map_project_record
from app.schemas.projects import ProjectCreate, ProjectUpdate
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
            # Send fields exactly matching the Pydantic schema snake_case as they correspond 
            # exactly to the Teable column names we defined in mapping.py 
            teable_fields = {k: v for k, v in fields.items() if v is not None}
                
            response = await self.client.create_record(self.table_id, teable_fields)
            # invalidate cache
            project_cache._cache.clear()
            return map_project_record(response.get("records", [])[0])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creando proyecto: {str(e)}")

    async def get_project_by_name(self, name: str):
        return await self.client.get_record_by_name(
            self.table_id,
            PROJECT_NAME_FIELD_ID,
            name,
        )

    async def update_project(self, project_id: str, project_data: ProjectUpdate):
        fields = project_data.model_dump(exclude_unset=True)
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
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error actualizando proyecto: {str(e)}")
