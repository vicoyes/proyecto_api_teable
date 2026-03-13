from typing import Any

from pydantic import BaseModel, ConfigDict


class CorreoResponse(BaseModel):
    """Un registro de correo electrónico (solo lectura)."""

    id: str
    date_iso: str | None = None
    from_name: str | None = None
    from_email: str | None = None
    to_email: str | None = None
    subject: str | None = None
    body_clean: str | None = None
    status: str | None = None
    proposed_reply: str | None = None
    approval_status: str | None = None
    approved_reply: str | None = None
    responded: bool | None = None
    thread_key: str | None = None
    notes: str | None = None
    ai_summary: str | None = None
    ai_sentiment: str | None = None
    ai_intent: str | None = None
    ai_priority: str | None = None
    ai_requires_reply: str | None = None
    ai_category: str | None = None
    remitente_original_email: str | None = None
    nombre_del_remitente_original: str | None = None
    Tipo: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CorreoUpdate(BaseModel):
    """Campos editables de un correo electrónico.

    No se permite crear correos nuevos desde la API, solo actualizar registros existentes.
    """

    date_iso: str | None = None
    from_name: str | None = None
    from_email: str | None = None
    to_email: str | None = None
    subject: str | None = None
    body_clean: str | None = None
    status: str | None = None
    proposed_reply: str | None = None
    approval_status: str | None = None
    approved_reply: str | None = None
    responded: bool | None = None
    thread_key: str | None = None
    notes: str | None = None
    ai_summary: str | None = None
    ai_sentiment: str | None = None
    ai_intent: str | None = None
    ai_priority: str | None = None
    ai_requires_reply: str | None = None
    ai_category: str | None = None
    remitente_original_email: str | None = None
    nombre_del_remitente_original: str | None = None
    Tipo: str | None = None


class CorreoListResponse(BaseModel):
    total: int
    items: list[CorreoResponse]
