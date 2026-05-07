# app/schemas/maestro.py
"""Esquemas para Maestro"""

from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional, List

class MaestroBase(BaseModel):
    """Base para Maestro"""
    nombre: str = Field(..., min_length=2, max_length=50)
    apellidos: str = Field(..., min_length=2, max_length=50)
    sexo: Optional[str] = Field(None, pattern="^(M|F|Otro)$")
    fecha_nacimiento: Optional[date] = None
    
    # Contacto
    email: EmailStr
    telefono: str = Field(..., pattern="^[0-9]{10,15}$")
    telefono_emergencia: Optional[str] = Field(None, pattern="^[0-9]{10,15}$")
    
    # Domicilio
    calle: Optional[str] = None
    numero: Optional[str] = None
    colonia: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = Field(None, pattern="^[0-9]{5}$")
    
    # Datos profesionales
    especialidad: Optional[str] = None
    grado: Optional[str] = None
    anos_experiencia: int = Field(0, ge=0, le=50)
    certificaciones: Optional[str] = None
    
    # Datos laborales
    fecha_contratacion: date = Field(default_factory=date.today)
    sueldo_base: float = Field(0.0, ge=0)
    comision_por_clase: float = Field(0.0, ge=0)
    activo: bool = True
    
    # Contacto emergencia
    contacto_emergencia_nombre: Optional[str] = None
    contacto_emergencia_parentesco: Optional[str] = None
    contacto_emergencia_telefono: Optional[str] = None

class MaestroCreate(MaestroBase):
    """Crear maestro"""
    pass

class MaestroUpdate(BaseModel):
    """Actualizar maestro"""
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    telefono_emergencia: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    colonia: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    especialidad: Optional[str] = None
    grado: Optional[str] = None
    anos_experiencia: Optional[int] = None
    certificaciones: Optional[str] = None
    fecha_contratacion: Optional[date] = None
    sueldo_base: Optional[float] = None
    comision_por_clase: Optional[float] = None
    activo: Optional[bool] = None
    contacto_emergencia_nombre: Optional[str] = None
    contacto_emergencia_parentesco: Optional[str] = None
    contacto_emergencia_telefono: Optional[str] = None

class MaestroResponse(MaestroBase):
    """Respuesta de maestro"""
    id: int
    nombre_completo: str
    horas_semana: int = 0
    alumnos_totales: int = 0
    notas: Optional[str] = None
    foto_url: Optional[str] = None
    
    class Config:
        from_attributes = True