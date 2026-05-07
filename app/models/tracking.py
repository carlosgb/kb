# app/models/tracking.py
"""Modelos para seguimiento histórico (peso, grados, técnicas, logros)"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import date
from typing import TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.alumno import AlumnoDB
    from app.models.evento import EventoDB
    from app.models.federacion import FederacionDB



class HistorialPesoDB(Base):
    """Historial de peso del alumno"""
    
    __tablename__ = "historial_pesos"
    
    id = Column(Integer, primary_key=True, index=True)
    peso = Column(Float, nullable=False)  # kg
    fecha = Column(Date, default=date.today, nullable=False)
    notas = Column(String, nullable=True)
    
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"))
    
    # Relaciones
    alumno = relationship("AlumnoDB", back_populates="pesos")
    
    def __repr__(self) -> str:
        return f"<HistorialPeso {self.peso}kg ({self.fecha})>"


class HistorialGradoDB(Base):
    """Historial de ascensos de grado/cinturón"""
    
    __tablename__ = "historial_grados"
    
    id = Column(Integer, primary_key=True, index=True)
    grado = Column(String, nullable=False)  # "Cinturón Amarillo", "Cinturón Verde", etc.
    fecha_ascenso = Column(Date, default=date.today, nullable=False)
    evaluador = Column(String, nullable=True)  # Quién evaluó
    notas = Column(Text, nullable=True)
    
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"))
    
    # Relaciones
    alumno = relationship("AlumnoDB", back_populates="grados")
    
    def __repr__(self) -> str:
        return f"<HistorialGrado {self.grado} ({self.fecha_ascenso})>"


class TecnicaDominadaDB(Base):
    """Técnicas dominadas por el alumno con nivel de dominio"""
    
    __tablename__ = "tecnicas_dominadas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_tecnica = Column(String, nullable=False)
    nivel_dominio = Column(Integer, default=1)  # 1-5 (1=Básico, 5=Experto)
    fecha_evaluacion = Column(Date, default=date.today)
    observaciones = Column(Text, nullable=True)
    
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"))
    
    # Relaciones
    alumno = relationship("AlumnoDB", back_populates="tecnicas")
    
    @property
    def nivel_texto(self) -> str:
        niveles = {1: "Básico", 2: "Intermedio bajo", 3: "Intermedio", 4: "Avanzado", 5: "Experto"}
        return niveles.get(self.nivel_dominio, "No definido")
    
    def __repr__(self) -> str:
        return f"<Tecnica {self.nombre_tecnica} - Nivel {self.nivel_dominio}>"


class LogroDB(Base):
    """Logros, medallas y reconocimientos del alumno"""
    
    __tablename__ = "logros"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Datos del logro
    torneo_nombre = Column(String, nullable=False)
    medalla = Column(String, nullable=False)  # "Oro", "Plata", "Bronce", "Participación", "Mención Honorífica"
    modalidad = Column(String, nullable=False)  # "Point Fighting", "Kick Light", "K1", "Full Contact", "Formas"
    categoria_peso = Column(String, nullable=True)
    fecha = Column(Date, default=date.today)
    
    # Puntos para ranking (opcional)
    puntos_ranking = Column(Integer, default=0)
    
    # Evidencia
    certificado_url = Column(String, nullable=True)
    foto_url = Column(String, nullable=True)
    notas = Column(Text, nullable=True)
    
    # Relaciones
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"))
    evento_id = Column(Integer, ForeignKey("eventos.id", ondelete="SET NULL"), nullable=True)
    federacion_id = Column(Integer, ForeignKey("federaciones.id", ondelete="SET NULL"), nullable=True)
    
    alumno = relationship("AlumnoDB", back_populates="logros")
    evento = relationship("EventoDB")
    federacion = relationship("FederacionDB")
    
    @property
    def medalla_icono(self) -> str:
        iconos = {
            "Oro": "🥇",
            "Plata": "🥈",
            "Bronce": "🥉",
            "Participación": "🎖️",
            "Mención Honorífica": "🏅"
        }
        return iconos.get(self.medalla, "🏆")
    
    def __repr__(self) -> str:
        return f"<Logro {self.medalla} en {self.torneo_nombre}>"