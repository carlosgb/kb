# app/models/expediente.py
"""Expediente médico, legal y de emergencia del alumno"""

from sqlalchemy import Column, Integer, String, Date, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date, timedelta
from typing import TYPE_CHECKING

from app.core.database import Base
from app.core.config import settings

if TYPE_CHECKING:
    from app.models.alumno import AlumnoDB



class ExpedienteDB(Base):
    """Expediente del alumno (datos sensibles, médicos, legales, emergencia)"""
    
    __tablename__ = "expedientes"
    
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"), unique=True)
    
    # === SALUD (Información clínica SENSIBLE) ===
    tipo_sangre = Column(String, nullable=True)  # "A+", "O-", etc.
    alergias = Column(Text, nullable=True)  # Alergias a medicamentos, alimentos, etc.
    condiciones_cronicas = Column(Text, nullable=True)  # Asma, diabetes, epilepsia, etc.
    medicamentos_actuales = Column(Text, nullable=True)  # Medicamentos que toma regularmente
    
    # === HISTORIAL MÉDICO ===
    lesiones_previas = Column(Text, nullable=True)  # Fracturas, cirugías previas
    cirugias = Column(Text, nullable=True)
    tratamientos_actuales = Column(Text, nullable=True)
    
    # === CONTACTO DE EMERGENCIA ===
    contacto_emergencia_nombre = Column(String, nullable=False)
    contacto_emergencia_parentesco = Column(String, nullable=True)  # "Madre", "Padre", "Tutor"
    contacto_emergencia_telefono = Column(String, nullable=False)
    contacto_emergencia_telefono_alt = Column(String, nullable=True)
    contacto_emergencia_email = Column(String, nullable=True)
    
    # === DATOS DEL MÉDICO FAMILIAR ===
    medico_familiar_nombre = Column(String, nullable=True)
    medico_familiar_telefono = Column(String, nullable=True)
    medico_familiar_cedula = Column(String, nullable=True)
    
    # === CERTIFICADO MÉDICO ===
    fecha_certificado_medico = Column(Date, nullable=True)
    nombre_medico_certifica = Column(String, nullable=True)
    cedula_profesional_medico = Column(String, nullable=True)
    clinica_hospital = Column(String, nullable=True)
    
    # === DOCUMENTOS LEGALES ===
    deslinde_firmado = Column(Boolean, default=False)
    deslinde_fecha = Column(Date, nullable=True)
    deslinde_url = Column(String, nullable=True)  # URL del documento escaneado
    
    reglamento_aceptado = Column(Boolean, default=False)
    reglamento_fecha = Column(Date, nullable=True)
    reglamento_url = Column(String, nullable=True)
    
    uso_imagen_autorizado = Column(Boolean, default=False)
    uso_imagen_fecha = Column(Date, nullable=True)
    uso_imagen_url = Column(String, nullable=True)
    
    # === AUTORIZACIÓN PARA MENORES ===
    autorizacion_paterna_firmada = Column(Boolean, default=False)
    autorizacion_paterna_fecha = Column(Date, nullable=True)
    nombre_tutor = Column(String, nullable=True)
    telefono_tutor = Column(String, nullable=True)
    tutor_relacion = Column(String, nullable=True)  # "Padre", "Madre", "Tío", etc.
    
    # === METADATA ===
    notas_medicas = Column(Text, nullable=True)
    notas_legales = Column(Text, nullable=True)
    fecha_actualizacion = Column(Date, default=date.today)
    
    # === RELACIONES ===
    alumno = relationship("AlumnoDB", back_populates="expediente")
    
    # === PROPIEDADES ===
    @property
    def certificado_vigente(self) -> bool:
        """Verifica si el certificado médico tiene menos de 365 días"""
        if not self.fecha_certificado_medico:
            return False
        return (date.today() - self.fecha_certificado_medico).days < settings.VIGENCIA_CERTIFICADO_MEDICO_DIAS
    
    @property
    def documentos_completos(self) -> bool:
        """Verifica si tiene todos los documentos obligatorios"""
        return all([
            self.deslinde_firmado,
            self.reglamento_aceptado,
            self.certificado_vigente
        ])
    
    @property
    def porcentaje_completado(self) -> int:
        """Porcentaje de completitud del expediente (útil para UI)"""
        campos = [
            self.tipo_sangre,
            self.contacto_emergencia_nombre,
            self.contacto_emergencia_telefono,
            self.fecha_certificado_medico,
            self.deslinde_firmado,
            self.reglamento_aceptado,
        ]
        llenos = sum(1 for c in campos if c)
        return int((llenos / len(campos)) * 100)
    
    def __repr__(self) -> str:
        return f"<Expediente Alumno ID: {self.alumno_id}>"