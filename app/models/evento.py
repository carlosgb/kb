# app/models/evento.py
"""Modelos para eventos, torneos y logística"""

from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import date
from typing import List, Optional, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.alumno import AlumnoDB
    from app.models.federacion import FederacionDB


class EventoDB(Base):
    """Eventos, torneos, seminarios, competencias"""
    
    __tablename__ = "eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Datos básicos
    titulo = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(String, nullable=False)
    lugar = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # "Torneo", "Seminario", "Exhibición", "Clase Magistral"
    
    # Descripción
    descripcion = Column(Text, nullable=True)
    
    # Organización
    organizador = Column(String, nullable=True)
    federacion_id = Column(Integer, ForeignKey("federaciones.id", ondelete="SET NULL"))
    
    # Reglas y requisitos
    sistema_reglas = Column(String, nullable=True)  # "WAKO", "IFMA", "K1", "Local"
    requiere_licencia = Column(Boolean, default=True)
    requiere_certificado_medico = Column(Boolean, default=True)
    
    # Costos
    costo_inscripcion = Column(Float, default=0.0)
    costo_acompañante = Column(Float, default=0.0)
    
    # Fechas clave
    fecha_cierre_inscripcion = Column(Date, nullable=True)
    fecha_publicacion_resultados = Column(Date, nullable=True)
    
    # Metadata
    activo = Column(Boolean, default=True)
    flyer_url = Column(String, nullable=True)
    reglamento_url = Column(String, nullable=True)
    
    # Relaciones
    federacion = relationship("FederacionDB")
    participantes = relationship("InscripcionEventoDB", back_populates="evento", cascade="all, delete-orphan")
    
    @property
    def total_inscritos(self) -> int:
        return len(self.participantes)
    
    @property
    def ingresos_estimados(self) -> float:
        total = 0.0
        for inscripcion in self.participantes:
            total += self.costo_inscripcion + (inscripcion.num_acompañantes * self.costo_acompañante)
        return total
    
    @property
    def total_pagados(self) -> int:
        return len([p for p in self.participantes if p.pagado])
    
    @property
    def inscripcion_abierta(self) -> bool:
        if not self.fecha_cierre_inscripcion:
            return True
        return date.today() <= self.fecha_cierre_inscripcion
    
    def __repr__(self) -> str:
        return f"<Evento {self.titulo} ({self.fecha})>"


class InscripcionEventoDB(Base):
    """Inscripción de un alumno a un evento"""
    
    __tablename__ = "inscripciones_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"))
    evento_id = Column(Integer, ForeignKey("eventos.id", ondelete="CASCADE"))
    
    # Datos de la inscripción
    num_acompañantes = Column(Integer, default=0)
    pagado = Column(Boolean, default=False)
    fecha_inscripcion = Column(Date, default=date.today)
    
    # Categoría en la que compite
    categoria_inscrita = Column(String, nullable=True)
    peso_registrado = Column(Float, nullable=True)  # Peso al momento de inscripción
    
    # Estado
    cancelada = Column(Boolean, default=False)
    motivo_cancelacion = Column(String, nullable=True)
    
    # Notas
    notas = Column(Text, nullable=True)
    
    # Relaciones
    alumno = relationship("AlumnoDB", back_populates="inscripciones_eventos")
    evento = relationship("EventoDB", back_populates="participantes")
    
    __table_args__ = (
        # No duplicar inscripciones
        UniqueConstraint('alumno_id', 'evento_id', name='unique_alumno_evento'),
    )
    
    @property
    def total_a_pagar(self) -> float:
        if not self.evento:
            return 0.0
        return self.evento.costo_inscripcion + (self.num_acompañantes * self.evento.costo_acompañante)
    
    @property
    def estado_pago_texto(self) -> str:
        return "Pagado" if self.pagado else "Pendiente"
    
    def __repr__(self) -> str:
        return f"<InscripcionEvento Alumno:{self.alumno_id} Evento:{self.evento_id}>"