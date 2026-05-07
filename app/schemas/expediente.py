# app/schemas/expediente.py
"""Esquemas para Expediente"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ExpedienteBase(BaseModel):
    """Base para Expediente"""
    # Salud
    tipo_sangre: Optional[str] = Field(None, pattern="^(A|B|AB|O)[+-]$")
    alergias: Optional[str] = None
    condiciones_cronicas: Optional[str] = None
    medicamentos_actuales: Optional[str] = None
    
    # Historial médico
    lesiones_previas: Optional[str] = None
    cirugias: Optional[str] = None
    tratamientos_actuales: Optional[str] = None
    
    # Contacto emergencia
    contacto_emergencia_nombre: str = Field(..., min_length=2)
    contacto_emergencia_parentesco: Optional[str] = None
    contacto_emergencia_telefono: str = Field(..., pattern="^[0-9]{10,15}$")
    contacto_emergencia_telefono_alt: Optional[str] = Field(None, pattern="^[0-9]{10,15}$")
    contacto_emergencia_email: Optional[str] = None
    
    # Médico familiar
    medico_familiar_nombre: Optional[str] = None
    medico_familiar_telefono: Optional[str] = None
    medico_familiar_cedula: Optional[str] = None
    
    # Certificado médico
    fecha_certificado_medico: Optional[date] = None
    nombre_medico_certifica: Optional[str] = None
    cedula_profesional_medico: Optional[str] = None
    clinica_hospital: Optional[str] = None
    
    # Documentos legales
    deslinde_firmado: bool = False
    deslinde_fecha: Optional[date] = None
    reglamento_aceptado: bool = False
    reglamento_fecha: Optional[date] = None
    uso_imagen_autorizado: bool = False
    uso_imagen_fecha: Optional[date] = None
    
    # Autorización menores
    autorizacion_paterna_firmada: bool = False
    autorizacion_paterna_fecha: Optional[date] = None
    nombre_tutor: Optional[str] = None
    telefono_tutor: Optional[str] = None
    tutor_relacion: Optional[str] = None

class ExpedienteUpdate(BaseModel):
    """Actualizar expediente (todos opcionales)"""
    tipo_sangre: Optional[str] = None
    alergias: Optional[str] = None
    condiciones_cronicas: Optional[str] = None
    medicamentos_actuales: Optional[str] = None
    lesiones_previas: Optional[str] = None
    cirugias: Optional[str] = None
    tratamientos_actuales: Optional[str] = None
    contacto_emergencia_nombre: Optional[str] = None
    contacto_emergencia_parentesco: Optional[str] = None
    contacto_emergencia_telefono: Optional[str] = None
    contacto_emergencia_telefono_alt: Optional[str] = None
    contacto_emergencia_email: Optional[str] = None
    medico_familiar_nombre: Optional[str] = None
    medico_familiar_telefono: Optional[str] = None
    medico_familiar_cedula: Optional[str] = None
    fecha_certificado_medico: Optional[date] = None
    nombre_medico_certifica: Optional[str] = None
    cedula_profesional_medico: Optional[str] = None
    clinica_hospital: Optional[str] = None
    deslinde_firmado: Optional[bool] = None
    deslinde_fecha: Optional[date] = None
    deslinde_url: Optional[str] = None
    reglamento_aceptado: Optional[bool] = None
    reglamento_fecha: Optional[date] = None
    reglamento_url: Optional[str] = None
    uso_imagen_autorizado: Optional[bool] = None
    uso_imagen_fecha: Optional[date] = None
    uso_imagen_url: Optional[str] = None
    autorizacion_paterna_firmada: Optional[bool] = None
    autorizacion_paterna_fecha: Optional[date] = None
    nombre_tutor: Optional[str] = None
    telefono_tutor: Optional[str] = None
    tutor_relacion: Optional[str] = None
    notas_medicas: Optional[str] = None
    notas_legales: Optional[str] = None

class ExpedienteResponse(ExpedienteBase):
    """Respuesta de expediente"""
    id: int
    alumno_id: int
    certificado_vigente: bool
    documentos_completos: bool
    porcentaje_completado: int
    fecha_actualizacion: date
    
    class Config:
        from_attributes = True