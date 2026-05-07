# app/schemas/alumno.py
"""Esquemas para Alumno"""

from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, List

from app.schemas.common import IdNameResponse

class AlumnoBase(BaseModel):
    """Base para Alumno"""
    nombre: str = Field(..., min_length=2, max_length=50)
    apellidos: str = Field(..., min_length=2, max_length=50)
    sexo: str = Field(..., pattern="^(M|F|Otro)$")
    fecha_nacimiento: date
    
    # Contacto
    email: Optional[str] = Field(None, max_length=100)
    telefono_celular: str = Field(..., pattern="^[0-9]{10,15}$")
    telefono_casa: Optional[str] = Field(None, pattern="^[0-9]{10,15}$")
    
    # Domicilio
    calle: str = Field(..., min_length=3)
    numero: Optional[str] = None
    colonia: Optional[str] = None
    ciudad: str = "Ciudad de México"
    codigo_postal: Optional[str] = Field(None, pattern="^[0-9]{5}$")
    
    # Datos físicos
    altura: float = Field(..., gt=0.5, lt=2.5, description="Altura en metros")
    peso_actual: float = Field(..., gt=10, lt=200, description="Peso en kg")
    
    # Datos deportivos
    grado_actual: str = "Principiante"
    es_competidor: bool = False
    
    # Datos escolares
    escuela: Optional[str] = None
    grado_escolar: Optional[str] = None
    
    # Control
    monto_mensualidad: float = Field(500.0, ge=0, le=5000)
    
    @field_validator('fecha_nacimiento')
    def validate_edad(cls, v):
        hoy = date.today()
        edad = hoy.year - v.year - ((hoy.month, hoy.day) < (v.month, v.day))
        if edad < 4:
            raise ValueError('El alumno debe tener al menos 4 años')
        if edad > 100:
            raise ValueError('Edad no válida')
        return v
    
    @field_validator('altura')
    def validate_altura(cls, v):
        if v < 0.5 or v > 2.5:
            raise ValueError('Altura debe estar entre 0.5m y 2.5m')
        return v
    
    @field_validator('peso_actual')
    def validate_peso(cls, v):
        if v < 10 or v > 200:
            raise ValueError('Peso debe estar entre 10kg y 200kg')
        return v

class AlumnoCreate(AlumnoBase):
    """Crear alumno"""
    pass

class AlumnoUpdate(BaseModel):
    """Actualizar alumno (todos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=50)
    sexo: Optional[str] = Field(None, pattern="^(M|F|Otro)$")
    fecha_nacimiento: Optional[date] = None
    email: Optional[str] = None
    telefono_celular: Optional[str] = None
    telefono_casa: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    colonia: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    altura: Optional[float] = Field(None, gt=0.5, lt=2.5)
    peso_actual: Optional[float] = Field(None, gt=10, lt=200)
    grado_actual: Optional[str] = None
    es_competidor: Optional[bool] = None
    escuela: Optional[str] = None
    grado_escolar: Optional[str] = None
    monto_mensualidad: Optional[float] = Field(None, ge=0, le=5000)
    activo: Optional[bool] = None

class AlumnoResponse(AlumnoBase):
    """Respuesta básica de alumno"""
    id: int
    categoria_wako: str
    categoria_generica: str
    categoria_actual: str
    edad: int
    imc: float
    asistencias_totales: int
    fecha_ultimo_pago: date
    estado_pago: str
    monto_con_recargo: float
    activo: bool
    fecha_registro: date
    
    class Config:
        from_attributes = True

class AlumnoDetailResponse(AlumnoResponse):
    """Respuesta detallada con relaciones"""
    membresia_activa: Optional[dict] = None
    seguro_activo: Optional[dict] = None
    tiene_expediente: bool = False
    expediente_completado: int = 0
    total_logros: int = 0
    total_tecnicas: int = 0
    
    class Config:
        from_attributes = True

class AlumnoListResponse(BaseModel):
    """Lista paginada de alumnos"""
    items: List[AlumnoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True