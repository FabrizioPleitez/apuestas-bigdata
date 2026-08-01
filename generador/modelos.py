from pydantic import BaseModel, Field
from typing import Literal
import uuid
from datetime import datetime, timezone


class Apuesta(BaseModel):
    apuesta_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partido_id: str
    usuario_id: str
    resultado_apostado: str
    monto: float
    cuota: float
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    canal: Literal["individual", "lote"] = "individual"


class ApuestaEntrada(BaseModel):
    """Lo que el cliente puede enviar; el resto se completa automáticamente."""
    partido_id: str
    resultado_apostado: str
    monto: float


class LoteRequest(BaseModel):
    cantidad: int = Field(gt=0, le=1_000_000)
    partido_id: str | None = None  # None = distribuye entre varios partidos