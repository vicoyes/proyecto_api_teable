# Documentación de la API de Tareas (Teable Proxy)

Esta API actúa como una capa semántica e intermediaria entre clientes externos (como agentes de IA o aplicaciones frontend) y el backend de **Teable**. Está construida utilizando **FastAPI** y sigue principios de arquitectura limpia y modular.

## Arquitectura del Proyecto

El proyecto está estructurado en capas para mantener una separación clara de responsabilidades:

- **Routers (`app/routers/`)**: Definen los endpoints de la API web, declaran los modelos de entrada y salida (usando Pydantic) y manejan la inyección de dependencias (por ejemplo, validación de API Key).
- **Services (`app/services/`)**: Contienen la lógica de negocio. Se encargan de procesar los datos recibidos de los routers, realizar mapeos o transformaciones necesarias (como resolver el ID de un usuario a partir de su nombre), y se comunican con el cliente de Teable.
- **Clients (`app/clients/`)**: Gestionan la comunicación de bajo nivel con servicios externos. En este caso, `TeableClient` utiliza `httpx` para realizar peticiones HTTP asíncronas a la API de Teable.
- **Schemas (`app/schemas/`)**: Modelos Pydantic que validan y serializan los datos tanto para las peticiones (Requests) como para las respuestas (Responses).
- **Utils (`app/utils/`)**: Utilidades generales, como el mapeo estandarizado de registros de Teable a schemas de Pydantic (`mapping.py`) y una caché en memoria básica (`cache.py`).

## Requisitos Previos e Instalación

### Variables de Entorno

El proyecto requiere un archivo `.env` en la raíz (puedes usar `.env.example` como plantilla) con al menos las siguientes variables:

```env
APP_NAME="Task API"
APP_ENV="production"
APP_DEBUG="false"
APP_PORT="8002"
APP_API_KEY="tu_clave_secreta" # Opcional. Si no se define, los endpoints serán públicos sin autenticación.

TEABLE_BASE_URL="https://plane.weavewp.com"
TEABLE_API_TOKEN="tu_token_de_teable"

TEABLE_TABLE_TASKS="tblcIYqqfI1gx8dCctA"
TEABLE_TABLE_TEAM="tblqbwuo04ZhdHq4Egm"
TEABLE_TABLE_PROJECTS="tblkdYU3GrAdAPHrajt"
```

### Despliegue en Producción (Docker / Portainer)

El `docker-compose.yml` base está optimizado para producción. Expone dinámicamente el puerto que especifiques y fija el puerto interno a `8000`. No monta volúmenes locales.

```bash
docker compose up -d --build
```

### Desarrollo Local (con Hot Reload)

Para desarrollo local, utiliza el archivo compose de desarrollo, el cual monta tu código fuente como volumen habilitando la recarga en caliente de uvicorn:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

---

## Referencia de la API (Endpoints)

La documentación interactiva en formato OpenAPI/Swagger está disponible en la ruta `/docs` (ej.: `http://localhost:8002/docs`) tras arrancar la API.

Toda ruta de negocio (todo bajo `/tasks`, `/team`, `/projects`, `/options`) requiere autenticación básica de cabecera si la variable `APP_API_KEY` está definida.

**Header requerido para autenticación:** `X-API-Key: tu_clave_secreta`

### 1. Sistema

`GET /health`
- **Descripción:** Comprueba si el contenedor de la API está vivo y levantado. No requiere autenticación.
- **Responde:** `{"status": "ok"}`

`GET /options`
- **Descripción:** Devuelve un diccionario estructurado (Ideal para poblar menús desplegables en UI o dar contexto a un agente IA) con todas las constantes válidas utilizadas en el negocio.
- **Responde:** Prioridades, Estados y Tipos de Tareas, Proyectos y Miembros.

### 2. Tareas (`/tasks`)

`GET /tasks`
- **Descripción:** Obtiene un listado paginado de tareas.
- **Query Params:** `skip` (int. default: 0), `take` (int, default: 50), `estado` (str, opcional).

`GET /tasks/{task_id}`
- **Descripción:** Obtiene el detalle unificado de una sola tarea identificada por su Record ID de Teable. Devuelve un error `404 Not Found` si no existe.

`POST /tasks`
- **Descripción:** Crea una nueva tarea.
- **Payload Requerido:** 
  - `nombre_tarea`: string (min 3 chars)
  - `prioridad`: BAJA | MEDIA | ALTA | CRÍTICA
  - `tipo_tarea`: OPERATIVA | TECNICA | ESTRATEGICA | etc.
- **Reglas de Negocio Automatizadas:** El cliente puede mandar el nombre en texto plano bajo la clave `responsable` (ej. "Héctor") o `proyecto` (ej. "Proyecto Alpha") y el backend buscará internamente en la DB el ID relacional de Teable antes de guardarlo.

`PATCH /tasks/{task_id}`
- **Descripción:** Permite modificar parcialmente cualquier atributo de una tarea.

`DELETE /tasks/{task_id}`
- **Descripción:** Elimina el registro de la tarea especificada de Teable permanentemente.

#### Endpoints de Acción (Atajos)

Diseñados para ejecutar operaciones de negocio recurrentes de forma ágil sin enviar un payload complejo:

- `POST /tasks/{task_id}/start`: Modifica el `estado_tarea` a `"EN_PROGRESO"`. Si la tarea no tenía `fecha_inicio`, automáticamente sella la fecha y hora UTC actual.
- `POST /tasks/{task_id}/complete`: Modifica el `estado_tarea` a `"COMPLETADA"`. Si la tarea no tenía `fecha_cierre`, automáticamente sella la fecha y hora UTC actual.
- `POST /tasks/{task_id}/block`: Modifica el `estado_tarea` a `"BLOQUEADA"`.

#### Resúmenes por Miembro

`GET /tasks/by-member/{member_name}`
- **Descripción:** Lista todas las tareas que han sido asignadas mediante Teable a un miembro en concreto realizando una búsqueda inversa.

`GET /tasks/by-member/{member_name}/summary`
- **Descripción:** Devuelve los conteos agregados de las tareas de un miembro por estado (Ej. Cuántas tiene En Progreso, Bloqueadas, etc.)

### 3. Equipo y Proyectos (`/team` y `/projects`)

`GET /team`
- **Descripción:** Lista los miembros disponibles en la base de datos de Teable. *Nota: Este endpoint tiene una caché de memoria (TTL: 5 min) para evitar golpear constantemente la API externa.*

`GET /projects`
- **Descripción:** Lista los proyectos vinculables registrados en Teable. *Nota: Este endpoint tiene una caché de memoria (TTL: 5 min).*

`POST /projects`
- **Descripción:** Crea un nuevo proyecto en Teable.
- **Payload Requerido:**
  - `nombre_proyecto`: string (min 3 chars)
- **Campos Opcionales:** `cliente`, `tipo_proyecto`, `estado_proyecto` (por defecto ACTIVO), `prioridad_proyecto` (por defecto MEDIA), `responsable_general`, `descripcion`, `fecha_inicio`, `fecha_fin`.

`PATCH /projects/{project_id}`
- **Descripción:** Permite modificar parcialmente los datos de un proyecto. Los campos son los mismos que en la creación, pero todos son opcionales.

---

## Logging

La aplicación incorpora un middleware HTTP nativo para exponer Logs Estructurados. 
Podrás visualizar los logs del tráfico ejecutando:
```bash
docker compose logs -f api
```
Cada línea será un bloque unilineal en formato JSON, indicando la URL, el método, el tiempo de proceso (`process_time_ms`) y el código de estado (`status_code`).
