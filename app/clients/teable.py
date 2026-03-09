import json
from datetime import date, datetime
from typing import Any

import httpx

from app.config import settings


class TeableClient:
    def __init__(self) -> None:
        self.base_url = settings.teable_base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {settings.teable_api_token}",
            "Content-Type": "application/json",
        }

    def _normalize_json_value(self, value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: self._normalize_json_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._normalize_json_value(item) for item in value]
        return value

    async def list_records(
        self,
        table_id: str,
        *,
        skip: int = 0,
        take: int = 100,
        search: str | None = None,
        filter_obj: dict[str, Any] | None = None,
        order_by: list[dict[str, Any]] | None = None,
        projection: list[str] | None = None,
    ) -> dict[str, Any]:
        params: list[tuple[str, str]] = [
            ("fieldKeyType", "name"),
            ("skip", str(skip)),
            ("take", str(take)),
        ]

        if search:
            params.append(("search", search))
        if filter_obj:
            params.append(("filter", json.dumps(filter_obj, ensure_ascii=False)))
        if order_by:
            params.append(("orderBy", json.dumps(order_by, ensure_ascii=False)))
        if projection:
            for field in projection:
                params.append(("projection", field))

        url = f"{self.base_url}/api/table/{table_id}/record"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def create_record(self, table_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/api/table/{table_id}/record"
        payload = {
            "fieldKeyType": "name",
            "records": [{"fields": self._normalize_json_value(fields)}],
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def update_record(self, table_id: str, record_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/api/table/{table_id}/record/{record_id}"
        payload = {
            "fieldKeyType": "name",
            "record": {"fields": self._normalize_json_value(fields)},
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def delete_record(self, table_id: str, record_id: str) -> dict[str, Any]:
        url = f"{self.base_url}/api/table/{table_id}/record/{record_id}"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_record(self, table_id: str, record_id: str) -> dict[str, Any]:
        url = f"{self.base_url}/api/table/{table_id}/record/{record_id}"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_record_by_name(
        self,
        table_id: str,
        field_id: str,
        value: str,
    ) -> dict[str, Any] | None:
        filter_obj = {
            "conjunction": "and",
            "filterSet": [
                {"fieldId": field_id, "operator": "is", "value": value},
            ],
        }
        data = await self.list_records(table_id, take=1, filter_obj=filter_obj)
        records = data.get("records", [])
        return records[0] if records else None
