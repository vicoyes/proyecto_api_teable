# Guía: Crear un endpoint nuevo para una tabla de Teable

Esta guía describe los pasos para exponer una **tabla de Teable** como endpoint(s) de la API, siguiendo la estructura existente del proyecto. Puedes crear solo endpoints **GET** (lectura) o un **CRUD completo**.

---

## Requisitos previos

- Tener el **Table ID** de la tabla en Teable (ej: `tblh4u4KrRK4NSiaWfJ`).
- Conocer los **nombres y tipos** de los campos (y, si vas a filtrar/ordenar, los **Field IDs** tipo `fldXXXX`).

---

## Resumen de pasos

| Paso | Archivo / Acción |
|------|------------------|
| 1 | Añadir variable de tabla en `config` y `.env` |
| 2 | Crear schemas en `app/schemas/` |
| 3 | Añadir función de mapeo en `app/utils/mapping.py` |
| 4 | Crear servicio en `app/services/` |
| 5 | Crear router en `app/routers/` |
| 6 | Registrar el router en `app/main.py` |

---

## 1. Configuración: tabla en config y `.env`

**`app/config.py`**

Añade la variable de la nueva tabla en la clase `Settings`:

```python
teable_table_mi_tabla: str  # nombre en snake_case, ej: teable_table_correos
```

**`.env` y `.env.example`**

Añade la variable con el Table ID de Teable:

```env
TEABLE_TABLE_MI_TABLA=tblXXXXXXXXXXXXXX
```

---

## 2. Schemas (`app/schemas/`)

Crea un archivo, por ejemplo `app/schemas/mi_tabla.py`.

- **Un modelo por registro** (lectura): todos los campos que devuelve la API, con tipos correctos (`str`, `int`, `bool`, `str | None`, etc.).
- **Un modelo para la lista**: `total` + lista de registros.

Ejemplo (solo lectura):

```python
from pydantic import BaseModel, ConfigDict


class MiTablaResponse(BaseModel):
    """Un registro de la tabla (solo lectura)."""
    id: str
    campo_a: str | None = None
    campo_b: int | None = None
    # ... resto de campos

    model_config = ConfigDict(from_attributes=True)


class MiTablaListResponse(BaseModel):
    total: int
    items: list[MiTablaResponse]
```

Si además quieres **crear** o **actualizar**, define `MiTablaCreate` y `MiTablaUpdate` con los campos editables (todos opcionales en Update).

---

## 3. Mapeo Teable → Schema (`app/utils/mapping.py`)

Teable devuelve registros con forma `{ "id": "...", "fields": { "nombre_campo": valor, ... } }`.  
Cuando usas `fieldKeyType=name`, las claves de `fields` son los **nombres** de los campos.

Añade una función que transforme un `record` de Teable en tu schema:

```python
from app.schemas.mi_tabla import MiTablaResponse

def map_mi_tabla_record(record: dict) -> MiTablaResponse:
    fields = record.get("fields", {})
    return MiTablaResponse(
        id=record["id"],
        campo_a=fields.get("campo_a"),
        campo_b=fields.get("campo_b"),
        # ... resto de campos (nombres tal como vienen de Teable)
    )
```

No olvides el **import** del nuevo schema al inicio del archivo.

---

## 4. Servicio (`app/services/`)

Crea `app/services/mi_tabla_service.py`.

- Usa `TeableClient()` y `settings.teable_table_mi_tabla`.
- **Listar**: `list_records()` con `skip`, `take` y, si aplica, `filter_obj`.
- **Filtrar**: en Teable los filtros usan **Field ID** (`fldXXX`), no el nombre. Construye algo como:

  ```python
  filter_obj = {
      "conjunction": "and",
      "filterSet": [
          {"fieldId": "fldXXXXXXXX", "operator": "is", "value": valor}
      ],
  }
  ```

- **Un registro por ID**: `client.get_record(table_id, record_id)` y luego tu función de mapeo.
- Maneja `httpx.HTTPStatusError` y devuelve `HTTPException` con código y mensaje adecuados (por ejemplo 404 si no existe).

Ejemplo mínimo (solo lectura: listar y obtener uno):

```python
import httpx
from fastapi import HTTPException, status

from app.clients.teable import TeableClient
from app.config import settings
from app.utils.mapping import map_mi_tabla_record

# Si filtras, define los Field IDs de Teable
FLD_MI_CAMPO = "fldXXXXXXXX"


class MiTablaService:
    def __init__(self) -> None:
        self.client = TeableClient()
        self.table_id = settings.teable_table_mi_tabla

    @staticmethod
    def _build_teable_error_detail(exc: httpx.HTTPStatusError, default_message: str) -> str:
        # ... (copia el mismo método de correo_service o cliente_service)
        pass

    async def list_mi_tabla(self, skip: int = 0, take: int = 100, mi_filtro: str | None = None):
        filter_obj = None
        if mi_filtro:
            filter_obj = {
                "conjunction": "and",
                "filterSet": [{"fieldId": FLD_MI_CAMPO, "operator": "is", "value": mi_filtro}],
            }
        data = await self.client.list_records(
            self.table_id, skip=skip, take=min(take, 1000), filter_obj=filter_obj
        )
        records = data.get("records", [])
        items = [map_mi_tabla_record(r) for r in records]
        return {"total": len(items), "items": items}

    async def get_mi_tabla(self, record_id: str):
        try:
            record = await self.client.get_record(self.table_id, record_id)
            return map_mi_tabla_record(record)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Registro no encontrado") from exc
            detail = self._build_teable_error_detail(exc, "Error obteniendo registro")
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
```

Para **crear/actualizar/eliminar**, usa `create_record`, `update_record` y `delete_record` del `TeableClient` y aplica el mismo patrón que en `cliente_service` o `correo_service`.

---

## 5. Router (`app/routers/`)

Crea `app/routers/mi_tabla.py`.

- **Prefijo**: por ejemplo `prefix="/mi-tabla"` (kebab-case en la URL).
- **Tags**: para agrupar en `/docs`.
- **Solo GET**: endpoints de lista y de detalle por `record_id`.
- **Con filtros**: parámetros opcionales con `Query(...)` (ej: `email`, `to_email`).

Ejemplo (solo lectura):

```python
from fastapi import APIRouter, Query

from app.schemas.mi_tabla import MiTablaListResponse, MiTablaResponse
from app.services.mi_tabla_service import MiTablaService

router = APIRouter(prefix="/mi-tabla", tags=["mi-tabla"])


@router.get("", response_model=MiTablaListResponse)
async def list_mi_tabla(
    skip: int = Query(0, ge=0),
    take: int = Query(100, ge=1, le=1000),
    mi_filtro: str | None = Query(None, description="Filtrar por campo X"),
):
    """Lista registros. Opcionalmente filtra por mi_filtro."""
    service = MiTablaService()
    return await service.list_mi_tabla(skip=skip, take=take, mi_filtro=mi_filtro)


@router.get("/{record_id}", response_model=MiTablaResponse)
async def get_mi_tabla(record_id: str):
    """Obtiene un registro por su ID."""
    service = MiTablaService()
    return await service.get_mi_tabla(record_id)
```

Si quieres CRUD completo, añade `POST ""`, `PATCH "/{record_id}"` y `DELETE "/{record_id}"` siguiendo el estilo de `app/routers/clientes.py`.

---

## 6. Registrar el router en `app/main.py`

1. Importa el router:

   ```python
   from app.routers.mi_tabla import router as mi_tabla_router
   ```

2. Regístralo con la misma autenticación que el resto (por ejemplo `verify_api_key`):

   ```python
   app.include_router(mi_tabla_router, dependencies=[Depends(verify_api_key)])
   ```

---

## Recordatorios importantes

- **Filtros y orden en Teable**: en los parámetros `filter` y `orderBy` de la API de Teable se usan **Field IDs** (`fldXXX`), no los nombres de los campos. Los nombres solo se usan en el body (POST/PATCH) cuando `fieldKeyType=name`.
- **Paginación**: `list_records` usa `skip` y `take`; en Teable el máximo de `take` suele ser 1000.
- **Operadores de filtro**: `is`, `isNot`, `contains`, `isEmpty`, etc. para texto; `isGreater`, `isLess`, etc. para números; `isBefore`, `isAfter`, `isWithin` para fechas.
- **Respuesta de listado**: el servicio puede devolver `{"total": len(items), "items": items}`; el `total` aquí es el número de ítems en la página actual. Si necesitas el total global, comprueba si la API de Teable lo devuelve en la respuesta de listado.

---

## Referencia rápida de archivos

| Concepto | Ejemplo en el proyecto |
|----------|-------------------------|
| Router solo GET | `app/routers/correos.py` |
| Router CRUD completo | `app/routers/clientes.py` |
| Servicio con filtros | `app/services/correo_service.py` |
| Schemas + list response | `app/schemas/correos.py`, `app/schemas/clientes.py` |
| Mapeo de registro | `map_correo_record` en `app/utils/mapping.py` |
| Cliente Teable | `app/clients/teable.py` (`list_records`, `get_record`, etc.) |

Con estos pasos puedes añadir de forma preestablecida un endpoint nuevo por cada tabla de Teable que quieras exponer en la API.
