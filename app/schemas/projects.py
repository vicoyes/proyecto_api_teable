from datetime import datetime
from typing import Literal

from pydantic import BaseModel


ProjectType = Literal[
    "CLIENTE",
    "INTERNO",
    "AUTOMATIZACION",
    "CONTENIDO",
    "INFRAESTRUCTURA",
    "PRODUCTO",
]
ProjectStatus = Literal["ACTIVO", "PAUSADO", "CERRADO", "CANCELADO"]
ProjectPriority = Literal["BAJA", "MEDIA", "ALTA", "CRÍTICA"]


class ProjectResponse(BaseModel):
    id: str
    nombre_proyecto: str
    cliente: str | None = None
    tipo_proyecto: ProjectType | None = None
    estado_proyecto: ProjectStatus | None = None
    prioridad_proyecto: ProjectPriority | None = None
    responsable_general: str | None = None
    descripcion: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None


class ProjectListResponse(BaseModel):
    total: int
    items: list[ProjectResponse]
