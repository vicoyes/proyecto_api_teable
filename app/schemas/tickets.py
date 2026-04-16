from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.schemas.tasks import LinkedRecordRef


TicketEstado = Literal[
    "Nuevo",
    "Planificado",
    "En ejecucion",
    "Completado",
    "Bloqueado",
    "Cancelado",
    "Aprobado",
]


def _optional_teable_text(v: Any) -> str | None:
    """Campo Teable single line text (`tiempo_estimado_horas`)."""
    if v is None:
        return None
    if isinstance(v, str):
        return v
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return str(v)
    return str(v)


def _optional_teable_number(v: Any) -> float | int | None:
    """Campos Teable number (`tiempo_estimado_horas_min` / `_max`)."""
    if v is None:
        return None
    if isinstance(v, bool):
        raise ValueError("no se acepta booleano en campos numéricos")
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return v
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        try:
            f = float(s)
            return int(f) if f.is_integer() else f
        except ValueError as exc:
            raise ValueError("número inválido") from exc
    raise TypeError("se esperaba número o texto numérico")


TeableTextOptional = Annotated[str | None, BeforeValidator(_optional_teable_text)]
TeableNumberOptional = Annotated[float | int | None, BeforeValidator(_optional_teable_number)]


class TicketResponse(BaseModel):
    id: str
    # Campo Teable "id" (número primario en la tabla)
    numero_ticket: float | int | None = None
    # Texto del single select en Teable; puede haber opciones no listadas en TicketEstado.
    estado: str | None = None
    titulo: str | None = None
    descripcion: str | None = None
    fecha_propuesta: str | None = None
    proyecto: LinkedRecordRef | None = None
    adjunto: Any | None = None
    resumen_ejecutivo: str | None = None
    nivel_urgencia: str | None = None
    departamento_principal: str | None = None
    perfiles_requeridos: str | None = None
    tiempo_estimado_horas: TeableTextOptional = None
    tiempo_estimado_horas_min: float | int | None = None
    tiempo_estimado_horas_max: float | int | None = None
    wbs_paso_1: str | None = None
    wbs_paso_2: str | None = None
    wbs_paso_3: str | None = None
    wbs_paso_4: str | None = None
    wbs_tareas_consolidado: str | None = None
    borrador_respuesta_cliente: str | None = None
    json_original: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TicketCreate(BaseModel):
    numero_ticket: float | int | None = Field(None, description='Valor del campo Teable "id" (número) si lo editas manualmente')
    estado: TicketEstado = Field(
        default="Nuevo",
        description="Por defecto Nuevo. Debe coincidir con el single select en Teable (campo Estado).",
    )
    titulo: str | None = None
    descripcion: str | None = None
    fecha_propuesta: str | None = None
    proyecto: str | None = Field(
        None,
        description="ID de registro Teable (rec…) o nombre exacto del proyecto (nombre_proyecto).",
    )
    adjunto: Any | None = Field(
        None,
        description="Adjuntos: estructura que acepte la API de Teable para el campo adjunto.",
    )
    resumen_ejecutivo: str | None = None
    nivel_urgencia: str | None = None
    departamento_principal: str | None = None
    perfiles_requeridos: str | None = None
    tiempo_estimado_horas: TeableTextOptional = None
    tiempo_estimado_horas_min: TeableNumberOptional = None
    tiempo_estimado_horas_max: TeableNumberOptional = None
    wbs_paso_1: str | None = None
    wbs_paso_2: str | None = None
    wbs_paso_3: str | None = None
    wbs_paso_4: str | None = None
    wbs_tareas_consolidado: str | None = None
    borrador_respuesta_cliente: str | None = None
    json_original: str | None = None


class TicketUpdate(BaseModel):
    numero_ticket: float | int | None = None
    estado: TicketEstado | None = None
    titulo: str | None = None
    descripcion: str | None = None
    fecha_propuesta: str | None = None
    proyecto: str | None = Field(
        None,
        description="ID de registro Teable (rec…) o nombre exacto del proyecto (nombre_proyecto).",
    )
    adjunto: Any | None = None
    resumen_ejecutivo: str | None = None
    nivel_urgencia: str | None = None
    departamento_principal: str | None = None
    perfiles_requeridos: str | None = None
    tiempo_estimado_horas: TeableTextOptional = None
    tiempo_estimado_horas_min: TeableNumberOptional = None
    tiempo_estimado_horas_max: TeableNumberOptional = None
    wbs_paso_1: str | None = None
    wbs_paso_2: str | None = None
    wbs_paso_3: str | None = None
    wbs_paso_4: str | None = None
    wbs_tareas_consolidado: str | None = None
    borrador_respuesta_cliente: str | None = None
    json_original: str | None = None


class TicketListResponse(BaseModel):
    total: int
    items: list[TicketResponse]
