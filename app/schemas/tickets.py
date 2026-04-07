from pydantic import BaseModel, ConfigDict, Field


class TicketResponse(BaseModel):
    id: str
    # Campo Teable "id" (número primario en la tabla)
    numero_ticket: float | int | None = None
    resumen_ejecutivo: str | None = None
    nivel_urgencia: str | None = None
    departamento_principal: str | None = None
    perfiles_requeridos: str | None = None
    tiempo_estimado_horas: float | None = None
    tiempo_estimado_horas_min: float | None = None
    tiempo_estimado_horas_max: float | None = None
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
    resumen_ejecutivo: str | None = None
    nivel_urgencia: str | None = None
    departamento_principal: str | None = None
    perfiles_requeridos: str | None = None
    tiempo_estimado_horas: float | None = None
    tiempo_estimado_horas_min: float | None = None
    tiempo_estimado_horas_max: float | None = None
    wbs_paso_1: str | None = None
    wbs_paso_2: str | None = None
    wbs_paso_3: str | None = None
    wbs_paso_4: str | None = None
    wbs_tareas_consolidado: str | None = None
    borrador_respuesta_cliente: str | None = None
    json_original: str | None = None


class TicketUpdate(BaseModel):
    numero_ticket: float | int | None = None
    resumen_ejecutivo: str | None = None
    nivel_urgencia: str | None = None
    departamento_principal: str | None = None
    perfiles_requeridos: str | None = None
    tiempo_estimado_horas: float | None = None
    tiempo_estimado_horas_min: float | None = None
    tiempo_estimado_horas_max: float | None = None
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
