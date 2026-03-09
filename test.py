import asyncio
import httpx
import json

base_url = "https://plane.weavewp.com"
token = "teable_accieHHMpcwxZeSreZR_eoG48DUNusNxFvkopAfvHJdOhDCniO/U0s8kBNLXDKM="
table_id = "tblkdYU3GrAdAPHrajt"
url = f"{base_url}/api/table/{table_id}/record"

payload1 = {
    "fieldKeyType": "name",
    "records": [{"fields": {"fields": {"Nombre_Proyecto": "Test"}}}]
}

payload2 = {
    "fieldKeyType": "name",
    "records": [{"fields": {"Nombre_Proyecto": "Test"}}]
}

async def run():
    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload1)
        print("Payload 1 (with nested fields):", r.status_code, r.text)
        
        r2 = await client.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload2)
        print("Payload 2 (correct):", r2.status_code, r2.text)

asyncio.run(run())
