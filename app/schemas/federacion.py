# app/schemas/federacion.py
"""Esquemas para Federaciones y Membresías"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class FederacionBase(BaseModel):
    """Base para Federación"""
    nombre: str = Field(..., min_length=2, max_length=50)
    nombre_completo: Optional[str] = None
    pais_origen: Optional[str] = None
    sitio_web: Optional[str] = None
    vigencia_dias: int = Field(365, ge=1, le=730)
    tiene_categorias_edad: bool = True
    tiene_categorias_peso: bool = True
    contacto_nombre: Optional[str] = None
    contacto_email: Optional[str] = None
    contacto_telefono: Optional[str] = None
    activo: bool = True

class FederacionCreate(FederacionBase):
    pass

class FederacionResponse(FederacionBase):
    id: int
    logo_url: Optional[str] = None
    alumnos_activos: int = 0
    
    class Config:
        from_attributes = True

class CategoriaFederacionBase(BaseModel):
    """Base para Categoría de Federación"""
    nombre: str = Field(..., min_length=2)
    codigo: Optional[str] = None
    edad_min: Optional[int] = Field(None, ge=0, le=100)
    edad_max: Optional[int] = Field(None, ge=0, le=100)
    peso_min: Optional[float] = Field(None, ge=0, le=200)
    peso_max: Optional[float] = Field(None, ge=0, le=200)
    genero: Optional[str] = Field(None, pattern="^(M|F|Mixed)$")
    descripcion: Optional[str] = None
    activo: bool = True

class CategoriaFederacionCreate(CategoriaFederacionBase):
    pass

class CategoriaFederacionResponse(CategoriaFederacionBase):
    id: int
    federacion_id: int
    rango_edad_texto: str
    rango_peso_texto: str
    
    class Config:
        from_attributes = True

class MembresiaFederacionBase(BaseModel):
    """Base para Membresía"""
    numero_afiliacion: str = Field(..., min_length=3)
    fecha_inicio: date = Field(default_factory=date.today)
    fecha_fin: Optional[date] = None
    costo_pagado: float = Field(0.0, ge=0)
    activa: bool = True

class MembresiaFederacionCreate(MembresiaFederacionBase):
    federacion_id: int

class MembresiaFederacionResponse(MembresiaFederacionBase):
    id: int
    alumno_id: int
    federacion_id: int
    federacion_nombre: str
    vigente: bool
    dias_restantes: int
    estado: str
    
    class Config:
        from_attributes = True