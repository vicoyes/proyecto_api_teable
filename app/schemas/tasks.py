from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


TaskPriority = Literal["BAJA", "MEDIA", "ALTA", "CRÍTICA"]
TaskStatus = Literal[
    "PENDIENTE",
    "EN_PROGRESO",
    "EN_REVISION",
    "BLOQUEADA",
    "COMPLETADA",
    "CANCELADA",
]
TaskType = Literal[
    "OPERATIVA",
    "TECNICA",
    "ESTRATEGICA",
    "CONTENIDO",
    "SOPORTE",
    "PERSONAL",
]


class TaskCreate(BaseModel):
    nombre_tarea: str = Field(..., min_length=3)
    prioridad: TaskPriority
    estado_tarea: TaskStatus = "PENDIENTE"
    tipo_tarea: TaskType
    fecha_limite: datetime | None = None
    fecha_inicio: datetime | None = None
    fecha_cierre: datetime | None = None
    hh_estimadas: float | None = None
    hh_reales: float | None = None
    notas: str | None = None
    correcciones: str | None = None
    resultado: str | None = None
    evidencias: str | None = None
    responsable: str | None = None
    proyecto: str | None = Field(
        None,
        description="ID de registro en Teable (rec…) o nombre exacto (campo nombre_proyecto).",
    )


class TaskUpdate(BaseModel):
    nombre_tarea: str | None = None
    prioridad: TaskPriority | None = None
    estado_tarea: TaskStatus | None = None
    tipo_tarea: TaskType | None = None
    fecha_limite: datetime | None = None
    fecha_inicio: datetime | None = None
    fecha_cierre: datetime | None = None
    hh_estimadas: float | None = None
    hh_reales: float | None = None
    notas: str | None = None
    correcciones: str | None = None
    resultado: str | None = None
    evidencias: str | None = None
    responsable: str | None = None
    proyecto: str | None = Field(
        None,
        description="ID de registro en Teable (rec…) o nombre exacto (campo nombre_proyecto).",
    )


class LinkedRecordRef(BaseModel):
    id: str
    title: str | None = None


class TaskResponse(BaseModel):
    id: str
    nombre_tarea: str | None = None
    prioridad: str | None = None
    estado_tarea: str | None = None
    tipo_tarea: str | None = None
    fecha_limite: datetime | None = None
    fecha_creacion: datetime | None = None
    fecha_inicio: datetime | None = None
    fecha_cierre: datetime | None = None
    hh_estimadas: float | None = None
    hh_reales: float | None = None
    notas: str | None = None
    correcciones: str | None = None
    resultado: str | None = None
    evidencias: str | None = None
    responsable: LinkedRecordRef | None = None
    proyecto: LinkedRecordRef | None = None

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    total: int
    items: list[TaskResponse]


class MemberTaskSummary(BaseModel):
    responsable: str
    counts: dict[str, int]
