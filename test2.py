import asyncio
import httpx
import json

base_url = "https://plane.weavewp.com"
token = "teable_accieHHMpcwxZeSreZR_eoG48DUNusNxFvkopAfvHJdOhDCniO/U0s8kBNLXDKM="
table_id = "tblkdYU3GrAdAPHrajt"
url = f"{base_url}/api/table/{table_id}/record"

payload2 = {
    "fieldKeyType": "name",
    "records": [{"fields": {"nombre_proyecto": "Test"}}]
}

async def run():
    async with httpx.AsyncClient() as client:
        r2 = await client.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload2)
        print("Payload:", r2.status_code, r2.text)

asyncio.run(run())
