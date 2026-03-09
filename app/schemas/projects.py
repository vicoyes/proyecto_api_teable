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
    nombre_proyecto: str | None = None
    descripcion: str | None = None
    estado_proyecto: str | None = None
    prioridad: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    presupuesto_estimado: float | None = None
    tipo_proyecto: str | None = None
    notas_internas: str | None = None
    
    model_config = ConfigDict(from_attributes=True)

class ProjectCreate(BaseModel):
    nombre_proyecto: str = Field(..., min_length=3, description="Nombre del proyecto")
    descripcion: str | None = None
    estado_proyecto: str | None = "ACTIVO"
    prioridad: str | None = "MEDIA"
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    presupuesto_estimado: float | None = None
    tipo_proyecto: str | None = None
    notas_internas: str | None = None


class ProjectListResponse(BaseModel):
    total: int
    items: list[ProjectResponse]
