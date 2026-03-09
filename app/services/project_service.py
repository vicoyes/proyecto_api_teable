from app.clients.teable import TeableClient
from app.config import settings
from app.utils.mapping import map_project_record


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

    async def get_project_by_name(self, name: str):
        return await self.client.get_record_by_name(
            self.table_id,
            PROJECT_NAME_FIELD_ID,
            name,
        )
