# Task API

API semántica sobre Teable para gestión de tareas, proyectos y equipo.

## Requisitos
- Python 3.11+
- Token válido de Teable

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Ejecutar con Docker (Recomendado)

```bash
docker compose up -d --build
```

La API estará disponible en `http://localhost:8002`

## Ejecutar localmente

```bash
uvicorn app.main:app --reload --port 8002
```

## Swagger

http://localhost:8002/docs

## Endpoints principales

### Health
- `GET /health`

### Tasks
- `GET /tasks`
- `POST /tasks`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `GET /tasks/by-member/{member_name}`
- `GET /tasks/by-member/{member_name}/summary`

### Team
- `GET /team`

### Projects
- `GET /projects`
