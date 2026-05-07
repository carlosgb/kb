# app/schemas/horario.py
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, List


class HorarioClaseBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50)
    tipo_clase: str = Field(..., pattern="^(Kick Light|Point Fighting|K1|Acondicionamiento|Infantil)$")
    nivel: str = Field("Mixto", pattern="^(Principiantes|Intermedios|Avanzados|Mixto)$")
    dia_semana: int = Field(..., ge=0, le=6)
    hora_inicio: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    hora_fin: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    capacidad_maxima: int = Field(20, ge=1, le=100)
    salon: str = "Main"
    maestro_id: Optional[int] = None
    activo: bool = True
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    
    @field_validator('hora_fin')
    @classmethod
    def validate_horario(cls, v, info):
        if 'hora_inicio' in info.data:
            inicio = info.data['hora_inicio']
            if inicio >= v:
                raise ValueError('hora_fin debe ser mayor que hora_inicio')
        return v


class HorarioClaseCreate(HorarioClaseBase):
    pass


class HorarioClaseUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo_clase: Optional[str] = None
    nivel: Optional[str] = None
    dia_semana: Optional[int] = Field(None, ge=0, le=6)
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    capacidad_maxima: Optional[int] = Field(None, ge=1, le=100)
    salon: Optional[str] = None
    maestro_id: Optional[int] = None
    activo: Optional[bool] = None
    color: Optional[str] = None


class HorarioClaseResponse(HorarioClaseBase):
    id: int
    nombre: str
    tipo_clase: str
    nivel: str
    dia_semana: int
    hora_inicio: str
    hora_fin: str
    capacidad_maxima: int
    salon: str
    maestro_id: Optional[int] = None
    activo: bool
    duracion_minutos: int = 0
    alumnos_inscritos: int = 0
    lugares_disponibles: int = 0
    esta_lleno: bool = False
    dia_nombre: str
    horario_texto: str
    maestro_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True

class InscripcionClaseCreate(BaseModel):
    """Inscribir alumno a clase"""
   
    asistencia_preferencial: bool = False
    notas: Optional[str] = None

class InscripcionClaseResponse(BaseModel):
    id: int
    alumno_id: int
    horario_id: int
    activo: bool
    fecha_inscripcion: date
    notas: Optional[str] = None
    alumno_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True

class AsistenciaAlumnoCreate(BaseModel):
    """Registrar asistencia de alumno"""
    horario_id: int
    alumno_id: int
    fecha_clase: date = Field(default_factory=date.today)
    presente: bool = True
    hora_llegada: Optional[str] = None
    minutos_tardia: int = 0
    observaciones: Optional[str] = None

class AsistenciaAlumnoResponse(BaseModel):
    id: int
    alumno_id: int
    horario_id: int
    fecha_clase: date
    presente: bool
    alumno_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True

class TomaAsistenciaMasiva(BaseModel):
    """Toma de asistencia masiva para una clase"""
    horario_id: int
    fecha_clase: date = Field(default_factory=date.today)
    presentes: List[int] = Field(default_factory=list, description="Lista de IDs de alumnos presentes")
    ausentes: List[int] = Field(default_factory=list, description="Lista de IDs de alumnos ausentes")