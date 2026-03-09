import asyncio
import httpx
import os
import json

async def main():
    token = os.environ.get('TEABLE_API_TOKEN')
    table_id = os.environ.get('TEABLE_TABLE_TASKS')
    headers = {
        'Authorization': f'Bearer {token}',
    }
    url = f'https://plane.weavewp.com/api/table/{table_id}/field'
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        print("Status Code:", res.status_code)
        if res.status_code == 200:
            fields = [{'id': f['id'], 'name': f['name'], 'type': f['type']} for f in res.json()]
            print('Available fields in Teable:\n', json.dumps(fields, indent=2))
        else:
            print(res.text)

if __name__ == '__main__':
    asyncio.run(main())
