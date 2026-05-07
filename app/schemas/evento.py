# app/schemas/evento.py
"""Esquemas para Eventos"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class EventoBase(BaseModel):
    """Base para Evento"""
    titulo: str = Field(..., min_length=3, max_length=100)
    fecha: date
    hora: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    lugar: str = Field(..., min_length=3)
    tipo: str = Field(..., pattern="^(Torneo|Seminario|Exhibición|Clase Magistral)$")
    descripcion: Optional[str] = None
    organizador: Optional[str] = None
    federacion_id: Optional[int] = None
    sistema_reglas: Optional[str] = None
    requiere_licencia: bool = True
    requiere_certificado_medico: bool = True
    costo_inscripcion: float = Field(0.0, ge=0)
    costo_acompañante: float = Field(0.0, ge=0)
    fecha_cierre_inscripcion: Optional[date] = None
    activo: bool = True

class EventoCreate(EventoBase):
    pass

class EventoUpdate(BaseModel):
    """Actualizar evento"""
    titulo: Optional[str] = None
    fecha: Optional[date] = None
    hora: Optional[str] = None
    lugar: Optional[str] = None
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    organizador: Optional[str] = None
    federacion_id: Optional[int] = None
    sistema_reglas: Optional[str] = None
    requiere_licencia: Optional[bool] = None
    requiere_certificado_medico: Optional[bool] = None
    costo_inscripcion: Optional[float] = None
    costo_acompañante: Optional[float] = None
    fecha_cierre_inscripcion: Optional[date] = None
    activo: Optional[bool] = None

class EventoResponse(EventoBase):
    id: int
    total_inscritos: int = 0
    ingresos_estimados: float = 0.0
    total_pagados: int = 0
    inscripcion_abierta: bool = True
    flyer_url: Optional[str] = None
    reglamento_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class InscripcionEventoCreate(BaseModel):
    num_acompañantes: int = 0
    categoria_inscrita: Optional[str] = None
    peso_registrado: Optional[float] = None


class InscripcionEventoResponse(BaseModel):
    id: int
    alumno_id: int
    alumno_nombre: Optional[str] = None
    evento_id: int
    evento_titulo: Optional[str] = None
    num_acompañantes: int
    pagado: bool
    total_a_pagar: float
    fecha_inscripcion: date
    cancelada: bool = False
    
    class Config:
        from_attributes = True