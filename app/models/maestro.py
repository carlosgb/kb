# app/models/maestro.py
"""Modelo de Maestro/Instructor"""

from sqlalchemy import Column, Integer, String, Float, Date, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from typing import List, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.horario import HorarioClaseDB, AsistenciaMaestroDB


class MaestroDB(Base):
    """Modelo de profesor/instructor"""
    
    __tablename__ = "maestros"
    
    # === IDENTIFICACIÓN ===
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    sexo = Column(String, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    
    # === CONTACTO ===
    email = Column(String, unique=True, index=True, nullable=False)
    telefono = Column(String, nullable=False)
    telefono_emergencia = Column(String, nullable=True)
    
    # === DOMICILIO ===
    calle = Column(String, nullable=True)
    numero = Column(String, nullable=True)
    colonia = Column(String, nullable=True)
    ciudad = Column(String, nullable=True)
    codigo_postal = Column(String, nullable=True)
    
    # === DATOS PROFESIONALES ===
    especialidad = Column(String, nullable=True)  # "Kick Light", "Point Fighting", "K1"
    grado = Column(String, nullable=True)  # "Cinturón Negro 1er Dan", etc.
    anos_experiencia = Column(Integer, default=0)
    certificaciones = Column(Text, nullable=True)  # JSON o texto con certificados
    
    # === DATOS LABORALES ===
    fecha_contratacion = Column(Date, default=date.today)
    sueldo_base = Column(Float, default=0.0)
    comision_por_clase = Column(Float, default=0.0)
    activo = Column(Boolean, default=True)
    
    # === METADATA ===
    notas = Column(Text, nullable=True)
    foto_url = Column(String, nullable=True)
    
    # === CONTACTO DE EMERGENCIA ===
    contacto_emergencia_nombre = Column(String, nullable=True)
    contacto_emergencia_parentesco = Column(String, nullable=True)
    contacto_emergencia_telefono = Column(String, nullable=True)
    
    # === RELACIONES ===
    horarios = relationship("HorarioClaseDB", back_populates="maestro")
    asistencias_dadas = relationship("AsistenciaMaestroDB", foreign_keys="[AsistenciaMaestroDB.maestro_id]", back_populates="maestro")    
    # === PROPIEDADES ===
    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellidos}"
    
    @property
    def horas_semana(self) -> int:
        """Total de horas que imparte a la semana"""
        return sum(h.duracion for h in self.horarios if h.activo) // 60 if self.horarios else 0
    
    @property
    def alumnos_totales(self) -> int:
        """Número total de alumnos únicos que asisten a sus clases"""
        alumnos_ids = set()
        for horario in self.horarios:
            for inscripcion in horario.inscripciones:
                if inscripcion.activo:
                    alumnos_ids.add(inscripcion.alumno_id)
        return len(alumnos_ids)
    
    def __repr__(self) -> str:
        return f"<Maestro {self.nombre_completo} (ID: {self.id})>"