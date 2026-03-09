from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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
    cliente: str | None = None
    tipo_proyecto: str | None = None
    estado_proyecto: str | None = None
    prioridad_proyecto: str | None = None
    responsable_general: str | None = None
    descripcion: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)

class ProjectCreate(BaseModel):
    nombre_proyecto: str = Field(..., min_length=3, description="Nombre del proyecto")
    cliente: str | None = None
    tipo_proyecto: str | None = None
    estado_proyecto: str | None = "ACTIVO"
    prioridad_proyecto: str | None = "MEDIA"
    responsable_general: str | None = None
    descripcion: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None


class ProjectUpdate(BaseModel):
    nombre_proyecto: str | None = Field(None, min_length=3)
    cliente: str | None = None
    tipo_proyecto: str | None = None
    estado_proyecto: str | None = None
    prioridad_proyecto: str | None = None
    responsable_general: str | None = None
    descripcion: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None


class ProjectListResponse(BaseModel):
    total: int
    items: list[ProjectResponse]
