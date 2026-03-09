import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    base_url = os.getenv("TEABLE_BASE_URL")
    token = os.getenv("TEABLE_API_TOKEN")
    table_id = os.getenv("TEABLE_TABLE_PROJECTS")
    
    url = f"{base_url}/api/table/{table_id}/record"
    print(url)
    payload = {
        "fieldKeyType": "name",
        "records": [{"fields": {"Nombre_Proyecto": "Test Project 123"}}]
    }
    
    async with httpx.AsyncClient() as client:
        re = await client.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload)
        print(re.status_code)
        print(re.text)

asyncio.run(test())
