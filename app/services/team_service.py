from app.clients.teable import TeableClient
from app.config import settings
from app.utils.mapping import map_team_record


from app.utils.cache import team_cache


TEAM_NAME_FIELD_ID = "fldddIJXn7MmezcIy5o"


class TeamService:
    def __init__(self) -> None:
        self.client = TeableClient()
        self.table_id = settings.teable_table_team

    async def list_members(self, skip: int = 0, take: int = 50):
        cache_key = f"list_members_{skip}_{take}"
        cached = team_cache.get(cache_key)
        if cached:
            return cached

        data = await self.client.list_records(self.table_id, skip=skip, take=take)
        items = [map_team_record(record) for record in data.get("records", [])]
        result = {"total": len(items), "items": items}
        team_cache.set(cache_key, result)
        return result

    async def get_member_by_name(self, name: str):
        return await self.client.get_record_by_name(
            self.table_id,
            TEAM_NAME_FIELD_ID,
            name,
        )
