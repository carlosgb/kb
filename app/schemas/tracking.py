# app/schemas/tracking.py
"""Esquemas para seguimiento histórico"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class HistorialPesoCreate(BaseModel):
    """Registrar peso"""
    peso: float = Field(..., gt=10, lt=200)
    fecha: date = Field(default_factory=date.today)
    notas: Optional[str] = None

class HistorialPesoResponse(BaseModel):
    id: int
    peso: float
    fecha: date
    notas: Optional[str] = None
    
    class Config:
        from_attributes = True

class HistorialGradoCreate(BaseModel):
    """Registrar ascenso de grado"""
    grado: str = Field(..., min_length=2)
    fecha_ascenso: date = Field(default_factory=date.today)
    evaluador: Optional[str] = None
    notas: Optional[str] = None

class HistorialGradoResponse(BaseModel):
    id: int
    grado: str
    fecha_ascenso: date
    evaluador: Optional[str] = None
    
    class Config:
        from_attributes = True

class TecnicaDominadaCreate(BaseModel):
    """Registrar técnica dominada"""
    nombre_tecnica: str = Field(..., min_length=2)
    nivel_dominio: int = Field(1, ge=1, le=5)
    observaciones: Optional[str] = None

class TecnicaDominadaResponse(BaseModel):
    id: int
    nombre_tecnica: str
    nivel_dominio: int
    nivel_texto: str
    fecha_evaluacion: date
    
    class Config:
        from_attributes = True

class LogroCreate(BaseModel):
    """Registrar logro/medalla"""
    torneo_nombre: str = Field(..., min_length=3)
    medalla: str = Field(..., pattern="^(Oro|Plata|Bronce|Participación|Mención Honorífica)$")
    modalidad: str = Field(..., min_length=2)
    categoria_peso: Optional[str] = None
    fecha: date = Field(default_factory=date.today)
    evento_id: Optional[int] = None
    federacion_id: Optional[int] = None
    puntos_ranking: int = Field(0, ge=0)
    certificado_url: Optional[str] = None
    foto_url: Optional[str] = None

class LogroResponse(LogroCreate):
    id: int
    alumno_id: int
    medalla_icono: str
    
    class Config:
        from_attributes = True