# app/models/horario.py
"""Modelos para horarios de clases, inscripciones y asistencias"""

from sqlalchemy import Column, Integer, String, Time, Date, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import date, time
from typing import Optional, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.alumno import AlumnoDB
    from app.models.maestro import MaestroDB


class HorarioClaseDB(Base):
    """Horario de clase recurrente (semanal)"""
    
    __tablename__ = "horarios_clase"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificación
    nombre = Column(String, nullable=False)  # "Kick Light Principiantes", "Competidores", etc.
    tipo_clase = Column(String, nullable=False)  # "Kick Light", "Point Fighting", "K1", "Acondicionamiento", "Infantil"
    nivel = Column(String, default="Mixto")  # "Principiantes", "Intermedios", "Avanzados", "Mixto"
    
    # Horario
    dia_semana = Column(Integer, nullable=False)  # 0=Lunes, 1=Martes, ..., 6=Domingo
    hora_inicio = Column(String, nullable=False)  # "09:00"
    hora_fin = Column(String, nullable=False)  # "10:30"
    duracion_minutos = Column(Integer, nullable=False)  # Calculado automáticamente
    
    # Capacidad
    capacidad_maxima = Column(Integer, default=20)
    salon = Column(String, default="Main")
    
    # Profesor
    maestro_id = Column(Integer, ForeignKey("maestros.id", ondelete="SET NULL"))
    
    # Estado
    activo = Column(Boolean, default=True)
    color = Column(String, nullable=True)  # Color para UI (ej: "#FF5733")
    
    # Relaciones
    maestro = relationship("MaestroDB", back_populates="horarios")
    inscripciones = relationship("InscripcionClaseDB", back_populates="horario", cascade="all, delete-orphan")
    asistencias = relationship("AsistenciaAlumnoDB", back_populates="horario")
    
    # === PROPIEDADES ===
    @property
    def alumnos_inscritos(self) -> int:
        return len([i for i in self.inscripciones if i.activo])
    
    @property
    def lugares_disponibles(self) -> int:
        return max(0, self.capacidad_maxima - self.alumnos_inscritos)
    
    @property
    def esta_lleno(self) -> bool:
        return self.lugares_disponibles == 0
    
    @property
    def dia_nombre(self) -> str:
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return dias[self.dia_semana] if 0 <= self.dia_semana < 7 else "Desconocido"
    
    @property
    def horario_texto(self) -> str:
        return f"{self.dia_nombre} {self.hora_inicio} - {self.hora_fin}"
    
    def __repr__(self) -> str:
        return f"<Horario {self.nombre} - {self.horario_texto}>"


class InscripcionClaseDB(Base):
    """Inscripción de un alumno a un horario de clase recurrente"""
    
    __tablename__ = "inscripciones_clase"
    
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"))
    horario_id = Column(Integer, ForeignKey("horarios_clase.id", ondelete="CASCADE"))
    
    # Fechas
    fecha_inscripcion = Column(Date, default=date.today)
    fecha_baja = Column(Date, nullable=True)
    
    # Estado
    activo = Column(Boolean, default=True)
    asistencia_preferencial = Column(Boolean, default=False)  # Prioridad en lista de espera
    
    # Notas
    notas = Column(Text, nullable=True)
    
    # Relaciones
    alumno = relationship("AlumnoDB", back_populates="inscripciones_clase")
    horario = relationship("HorarioClaseDB", back_populates="inscripciones")
    
    __table_args__ = (
        UniqueConstraint('alumno_id', 'horario_id', name='unique_alumno_horario'),
    )
    
    @property
    def activo_str(self) -> str:
        return "Activo" if self.activo else "Dado de baja"
    
    def __repr__(self) -> str:
        return f"<InscripcionClase Alumno:{self.alumno_id} Horario:{self.horario_id}>"


class AsistenciaAlumnoDB(Base):
    """Registro de asistencia diaria por alumno y clase"""
    
    __tablename__ = "asistencias_alumno"
    
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"))
    horario_id = Column(Integer, ForeignKey("horarios_clase.id", ondelete="CASCADE"))
    
    fecha_clase = Column(Date, default=date.today, nullable=False)
    presente = Column(Boolean, default=True)
    
    # Registro de tiempo
    hora_llegada = Column(String, nullable=True)  # "18:35"
    minutos_tardia = Column(Integer, default=0)
    
    # Observaciones
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    alumno = relationship("AlumnoDB", back_populates="asistencias")
    horario = relationship("HorarioClaseDB", back_populates="asistencias")
    
    __table_args__ = (
        UniqueConstraint('alumno_id', 'horario_id', 'fecha_clase', 
                        name='unique_asistencia_diaria'),
    )
    
    @property
    def estado_texto(self) -> str:
        return "Presente" if self.presente else "Ausente"
    
    def __repr__(self) -> str:
        return f"<Asistencia {self.fecha_clase} - {self.estado_texto}>"


class AsistenciaMaestroDB(Base):
    """Registro de asistencia del maestro a sus clases"""
    
    __tablename__ = "asistencias_maestro"
    
    id = Column(Integer, primary_key=True, index=True)
    maestro_id = Column(Integer, ForeignKey("maestros.id", ondelete="CASCADE"))
    horario_id = Column(Integer, ForeignKey("horarios_clase.id", ondelete="CASCADE"))
    
    fecha_clase = Column(Date, default=date.today, nullable=False)
    presente = Column(Boolean, default=True)
    
    hora_llegada = Column(String, nullable=True)
    notas = Column(Text, nullable=True)
    
    # Sustitución
    sustituto_id = Column(Integer, ForeignKey("maestros.id"), nullable=True)
    es_suplente = Column(Boolean, default=False)
    
    # Relaciones
    maestro = relationship("MaestroDB", foreign_keys=[maestro_id], back_populates="asistencias_dadas")
    sustituto = relationship("MaestroDB", foreign_keys=[sustituto_id])
    horario = relationship("HorarioClaseDB")
    
    __table_args__ = (
        UniqueConstraint('maestro_id', 'horario_id', 'fecha_clase', 
                        name='unique_asistencia_maestro_diaria'),
    )
    
    def __repr__(self) -> str:
        return f"<AsistenciaMaestro {self.fecha_clase} - {self.maestro.nombre_completo}>"