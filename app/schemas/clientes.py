from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ClienteResponse(BaseModel):
    id: str
    etiqueta: str | None = None
    nombre_del_cliente: str | None = None
    email: str | None = None
    empresa: str | None = None
    numero_de_telefono: str | None = None
    notas: str | None = None
    
    model_config = ConfigDict(from_attributes=True)

class ClienteCreate(BaseModel):
    etiqueta: str = Field(..., description="Etiqueta principal del cliente")
    nombre_del_cliente: str | None = None
    email: str | None = None
    empresa: str | None = None
    numero_de_telefono: str | None = None
    notas: str | None = None

class ClienteUpdate(BaseModel):
    etiqueta: str | None = None
    nombre_del_cliente: str | None = None
    email: str | None = None
    empresa: str | None = None
    numero_de_telefono: str | None = None
    notas: str | None = None

class ClienteListResponse(BaseModel):
    total: int
    items: list[ClienteResponse]
