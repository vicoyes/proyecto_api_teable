from typing import Literal

from pydantic import BaseModel, Field


TeamMemberType = Literal["HUMANO", "AGENTE_IA", "EXTERNO"]
TeamMemberStatus = Literal["ACTIVO", "INACTIVO"]


class TeamMemberResponse(BaseModel):
    id: str
    nombre: str
    tipo_miembro: TeamMemberType | None = None
    rol: str | None = None
    especialidad: str | None = None
    estado: TeamMemberStatus | None = None
    capacidad_horas: float | None = None
    canal_contacto: str | None = None
    notas: str | None = None


class TeamListResponse(BaseModel):
    total: int
    items: list[TeamMemberResponse]
