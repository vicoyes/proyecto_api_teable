# Tickets — Guía de uso de la API

Esta guía describe el recurso **Tickets** de la API: proxy sobre la tabla **tickets** en Teable. Sirve para que integradores, frontends u otros equipos sepan qué enviar, qué esperar y cómo se relaciona con Teable.

## Autenticación y base URL

- **Base:** la misma que el resto de la API (por ejemplo `http://localhost:8002` o tu dominio).
- **Swagger:** `GET /docs` — sección **tickets**.
- Si en el servidor está definida **`APP_API_KEY`**, todas las rutas bajo `/tickets` requieren la cabecera:
  ```http
  X-API-Key: <tu_clave>
  ```

## Configuración (Teable)

| Variable de entorno | Descripción |
|---------------------|-------------|
| `TEABLE_BASE_URL` | URL base de Teable (ej. `https://plane.weavewp.com`). |
| `TEABLE_API_TOKEN` | Token con permisos sobre la tabla. |
| `TEABLE_TABLE_TICKETS` | ID de la tabla en Teable (por defecto en código: `tblF4h8mUQKVNmUR9a8`). |

La API escribe en Teable con **`fieldKeyType=name`**: los nombres de campo en el cuerpo deben coincidir con los de la tabla (salvo los que esta API renombra por comodidad; ver más abajo).

## Identificadores

| Concepto | En la API | En Teable |
|----------|-----------|-----------|
| Identificador del **registro** (fila) | `id` en las respuestas | Record ID tipo `recXXXXXXXX` |
| Número primario de la tabla (campo numérico) | `numero_ticket` en JSON | Campo cuyo nombre en tabla es **`id`** |

- En **GET**, **PATCH** y **DELETE** la ruta usa el **record id** de Teable (`rec…`), no el número `numero_ticket`.

## Campo `estado` (single select)

En Teable el campo se llama **`Estado`**. En la API usas la clave **`estado`** (minúsculas).

**Valores habituales** en la API (deben existir igual como opciones del single select en Teable):

| Valor API |
|-----------|
| `Nuevo` |
| `Planificado` |
| `En ejecucion` |
| `Completado` |
| `Bloqueado` |
| `Cancelado` |
| `Aprobado` |

En **respuestas** (`GET`…), `estado` es siempre el texto que devuelve Teable: si añades opciones nuevas al select, la lista seguirá funcionando sin cambiar código.

- **Crear (`POST`):** si no envías `estado`, la API aplica por defecto **`Nuevo`** y lo persiste en Teable.
- **Actualizar (`PATCH`):** solo cambia `estado` si lo incluyes en el cuerpo.

## Endpoints

### `GET /tickets`

Lista tickets con paginación y búsqueda opcional en Teable.

| Query | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `skip` | int | `0` | Registros a saltar. |
| `take` | int | `50` | Tamaño de página (máx. `1000`). |
| `search` | string | — | Búsqueda global en campos (comportamiento Teable). |

**Respuesta (`200`):** objeto con `total` (número de ítems en esta página) e `items` (array de tickets).

---

### `GET /tickets/{ticket_id}`

Obtiene un ticket por **record id** Teable (`rec…`).

- **200:** un objeto ticket.
- **404:** `{"detail": "Ticket no encontrado"}`.

---

### `POST /tickets`

Crea un registro. **No hay campos obligatorios** en el schema: puedes enviar solo los que necesites; el resto queda vacío en Teable salvo **`estado`**, que por defecto es **`Nuevo`** si omites la clave.

**Respuesta:** `201 Created` con el ticket creado (incluye `id` del nuevo registro).

---

### `PATCH /tickets/{ticket_id}`

Actualización parcial. Solo se envían los campos que quieras modificar.

- **400** si el cuerpo está vacío (no hay nada que actualizar).

---

### `DELETE /tickets/{ticket_id}`

Elimina el registro en Teable.

**Respuesta (`200`):** `{"message": "Ticket eliminado correctamente"}`.

---

## Campos del cuerpo (crear / actualizar)

Todos son opcionales en el schema; en **PATCH** solo manda los que cambien.

| Clave API | Tipo | Notas |
|-----------|------|--------|
| `numero_ticket` | number | Se mapea al campo Teable **`id`** (número). Si en Teable es autogenerado, puede no ser necesario enviarlo al crear. |
| `estado` | string | Ver tabla de valores arriba. Default en **POST:** `Nuevo`. |
| `titulo` | string | Se guarda en Teable como **`Titulo`**. |
| `descripcion` | string | Texto largo; en Teable el campo se llama **`Descripcion `** (con espacio final). |
| `fecha_propuesta` | string | En Teable: **`Fecha_propuesta`** (texto). |
| `proyecto` | string | Nombre exacto del proyecto o ID `rec…`; la API resuelve el enlace (campo Teable **`proyecto`**). |
| `adjunto` | JSON | Archivos adjuntos según formato que acepte Teable para el campo **`adjunto`**; consulta la API de Teable para subir ficheros. |
| `resumen_ejecutivo` | string | |
| `nivel_urgencia` | string | |
| `departamento_principal` | string | |
| `perfiles_requeridos` | string | |
| `tiempo_estimado_horas` | string | En Teable: **single line text** (`fldzLiHmauMIR7JTKtW`). Ej. `"4-6"`. Si en JSON mandas número, se convierte a string. |
| `tiempo_estimado_horas_min` | number | En Teable: **number** (`fldtdp4atP4R36hx0iB`). |
| `tiempo_estimado_horas_max` | number | En Teable: **number** (`fld3WvQPyDMuRNh8t5a`). |
| `wbs_paso_1` … `wbs_paso_4` | string | |
| `wbs_tareas_consolidado` | string | |
| `borrador_respuesta_cliente` | string | Texto largo en Teable. |
| `json_original` | string | Texto largo (JSON serializado como string). |

### Objeto de respuesta (`TicketResponse`)

Incluye **`id`** (record `rec…`), **`numero_ticket`** (valor del campo numérico `id` en Teable), **`proyecto`** como objeto `{ id, title }` si hay enlace, **`adjunto`** tal como devuelve Teable, y el resto de campos según lo almacenado. El campo **`estado`** se devuelve como **string** con el valor exacto del single select en Teable (no se limita al enum de **POST/PATCH**).

---

## Ejemplos

### Listar con paginación

```bash
curl -s "http://127.0.0.1:8002/tickets?skip=0&take=10" \
  -H "X-API-Key: tu_clave"
```

### Crear (estado por defecto Nuevo)

```bash
curl -s -X POST "http://127.0.0.1:8002/tickets" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu_clave" \
  -d '{"resumen_ejecutivo":"Solicitud de soporte","nivel_urgencia":"alta"}'
```

### Crear con estado explícito

```bash
curl -s -X POST "http://127.0.0.1:8002/tickets" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu_clave" \
  -d '{"estado":"Planificado","resumen_ejecutivo":"Ticket planificado"}'
```

### Actualizar solo estado

```bash
curl -s -X PATCH "http://127.0.0.1:8002/tickets/recXXXXXXXXXXXXXX" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu_clave" \
  -d '{"estado":"En ejecucion"}'
```

### Eliminar

```bash
curl -s -X DELETE "http://127.0.0.1:8002/tickets/recXXXXXXXXXXXXXX" \
  -H "X-API-Key: tu_clave"
```

---

## Errores habituales

| Situación | Respuesta típica |
|-----------|-------------------|
| Record id inválido o borrado | `404` |
| Validación (estado no permitido, tipo incorrecto) | `422` con detalle de Pydantic |
| Teable rechaza el valor (opción inexistente en single select) | `4xx/5xx` con mensaje de Teable en `detail` |
| `PATCH` sin ningún campo | `400` "No se enviaron campos para actualizar" |

---

## Referencia rápida OpenAPI

La fuente de verdad de tipos y enums es el código (`app/schemas/tickets.py`) y la UI **`/docs`**, generada automáticamente por FastAPI.
