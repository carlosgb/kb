# app/schemas/seguro.py
"""Esquemas para Seguros"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class AseguradoraBase(BaseModel):
    """Base para Aseguradora"""
    nombre: str = Field(..., min_length=2)
    razon_social: Optional[str] = None
    rfc: Optional[str] = Field(None, pattern="^[A-Z&Ñ]{3,4}[0-9]{6}[A-Z0-9]{3}$")
    telefono_contacto: Optional[str] = None
    email_contacto: Optional[str] = None
    sitio_web: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool = True
    comision_porcentaje: float = Field(0.0, ge=0, le=100)


class AseguradoraCreate(AseguradoraBase):
    pass

class AseguradoraUpdate(BaseModel):
    nombre: Optional[str] = None
    razon_social: Optional[str] = None
    rfc: Optional[str] = None
    telefono_contacto: Optional[str] = None
    email_contacto: Optional[str] = None
    sitio_web: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None
    comision_porcentaje: Optional[float] = None

class AseguradoraResponse(AseguradoraBase):
    id: int
    
    class Config:
        from_attributes = True

class PolizaSeguroBase(BaseModel):
    """Base para Póliza"""
    numero_poliza: str = Field(..., min_length=3)
    nombre_plan: str = Field(..., min_length=2)
    cobertura_medica_max: float = Field(0.0, ge=0)
    cobertura_incapacidad: float = Field(0.0, ge=0)
    cobertura_muerte: float = Field(0.0, ge=0)
    cobertura_dental: float = Field(0.0, ge=0)
    cobertura_ambulancia: float = Field(0.0, ge=0)
    deducible: float = Field(0.0, ge=0)
    copago_porcentaje: float = Field(0.0, ge=0, le=100)
    exclusiones: Optional[str] = None
    condiciones_especiales: Optional[str] = None
    fecha_inicio_vigencia: date
    fecha_fin_vigencia: date
    costo_mensual_por_alumno: float = Field(0.0, ge=0)
    costo_anual_por_alumno: float = Field(0.0, ge=0)
    activa: bool = True

class PolizaSeguroCreate(PolizaSeguroBase):
    pass


class PolizaSeguroUpdate(BaseModel):
    aseguradora_id: Optional[int] = None
    numero_poliza: Optional[str] = None
    nombre_plan: Optional[str] = None
    cobertura_medica_max: Optional[float] = None
    cobertura_incapacidad: Optional[float] = None
    cobertura_muerte: Optional[float] = None
    cobertura_dental: Optional[float] = None
    cobertura_ambulancia: Optional[float] = None
    deducible: Optional[float] = None
    copago_porcentaje: Optional[float] = None
    exclusiones: Optional[str] = None
    condiciones_especiales: Optional[str] = None
    fecha_inicio_vigencia: Optional[date] = None
    fecha_fin_vigencia: Optional[date] = None
    costo_mensual_por_alumno: Optional[float] = None
    costo_anual_por_alumno: Optional[float] = None
    activa: Optional[bool] = None

class PolizaSeguroResponse(PolizaSeguroBase):
    id: int
    aseguradora_id: int
    aseguradora_nombre: str
    vigente: bool
    
    class Config:
        from_attributes = True

class ContratoSeguroBase(BaseModel):
    """Base para Contrato de Seguro"""
    numero_certificado: str = Field(..., min_length=3)
    fecha_inicio: date = Field(default_factory=date.today)
    fecha_fin: date
    prima_pagada: float = Field(0.0, ge=0)
    forma_pago: str = Field("Anual", pattern="^(Mensual|Trimestral|Anual|Incluido)$")
    activo: bool = True

class ContratoSeguroCreate(ContratoSeguroBase):
    poliza_id: int

class ContratoSeguroResponse(ContratoSeguroBase):
    id: int
    alumno_id: int
    poliza_id: int
    poliza_nombre: str
    aseguradora_nombre: str
    vigente: bool
    dias_restantes: int
    cobertura_resumida: dict
    
    class Config:
        from_attributes = True

class SiniestroSeguroBase(BaseModel):
    """Base para Siniestro"""
    fecha_accidente: date
    descripcion: str = Field(..., min_length=5)
    lugar_accidente: Optional[str] = None
    parte_del_cuerpo: Optional[str] = None
    diagnostico: Optional[str] = None
    gastos_totales: float = Field(0.0, ge=0)
    monto_cubierto: float = Field(0.0, ge=0)
    monto_deducible: float = Field(0.0, ge=0)
    monto_no_cubierto: float = Field(0.0, ge=0)

class SiniestroSeguroCreate(SiniestroSeguroBase):
    pass

class SiniestroSeguroResponse(SiniestroSeguroBase):
    id: int
    contrato_id: int
    estado: str
    numero_siniestro: str
    fecha_reporte: date
    fecha_resolucion: Optional[date] = None
    
    class Config:
        from_attributes = True