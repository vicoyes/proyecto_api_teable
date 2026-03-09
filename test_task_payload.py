import asyncio
import httpx
import os

async def main():
    token = os.environ.get('TEABLE_API_TOKEN')
    table_id = os.environ.get('TEABLE_TABLE_TASKS')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    url = f'https://plane.weavewp.com/api/table/{table_id}/record'
    payload = {
        "fieldKeyType": "name",
        "records": [
            {
                "fields": {
                    "nombre_tarea": "Prueba de Debug",
                    "prioridad": "MEDIA",
                    "tipo_tarea": "OPERATIVA",
                    "estado_tarea": "PENDIENTE",
                }
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=payload)
        print("Status", res.status_code)
        print("Message", res.text)

if __name__ == '__main__':
    asyncio.run(main())
