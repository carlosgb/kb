# app/models/federacion.py
"""Modelos para gestión de federaciones (WAKO, IFMA, etc.)"""

from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import date, timedelta
from typing import Optional, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from .alumno import AlumnoDB


class FederacionDB(Base):
    """Federación u organización deportiva (WAKO, IFMA, ISKA, etc.)"""
    
    __tablename__ = "federaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)  # "WAKO", "IFMA"
    nombre_completo = Column(String, nullable=True)  # Nombre legal completo
    pais_origen = Column(String, nullable=True)
    sitio_web = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    
    # Configuración
    vigencia_dias = Column(Integer, default=365)  # Días que dura la membresía
    tiene_categorias_edad = Column(Boolean, default=True)
    tiene_categorias_peso = Column(Boolean, default=True)
    
    # Contacto
    contacto_nombre = Column(String, nullable=True)
    contacto_email = Column(String, nullable=True)
    contacto_telefono = Column(String, nullable=True)
    
    # Estado
    activo = Column(Boolean, default=True)
    
    # Relaciones
    membresias = relationship("MembresiaFederacionDB", back_populates="federacion", cascade="all, delete-orphan")
    categorias = relationship("CategoriaFederacionDB", back_populates="federacion", cascade="all, delete-orphan")
    
    @property
    def alumnos_activos(self) -> int:
        return sum(1 for m in self.membresias if m.vigente)
    
    def __repr__(self) -> str:
        return f"<Federacion {self.nombre}>"


class CategoriaFederacionDB(Base):
    """Categorías por federación (rangos de edad/peso)"""
    
    __tablename__ = "categorias_federacion"
    
    id = Column(Integer, primary_key=True, index=True)
    federacion_id = Column(Integer, ForeignKey("federaciones.id", ondelete="CASCADE"))
    
    nombre = Column(String, nullable=False)  # "Senior Male -74kg"
    codigo = Column(String, nullable=True)   # "SEN-M-74"
    
    # Rangos de edad
    edad_min = Column(Integer, nullable=True)
    edad_max = Column(Integer, nullable=True)
    
    # Rangos de peso (kg)
    peso_min = Column(Float, nullable=True)
    peso_max = Column(Float, nullable=True)
    
    # Género permitido
    genero = Column(String, nullable=True)  # "M", "F", "Mixed"
    
    # Metadata
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    federacion = relationship("FederacionDB", back_populates="categorias")
    
    @property
    def rango_edad_texto(self) -> str:
        if self.edad_min and self.edad_max:
            return f"{self.edad_min}-{self.edad_max} años"
        elif self.edad_min:
            return f"+{self.edad_min} años"
        elif self.edad_max:
            return f"-{self.edad_max} años"
        return "Sin límite"
    
    @property
    def rango_peso_texto(self) -> str:
        if self.peso_min and self.peso_max:
            return f"{self.peso_min}-{self.peso_max} kg"
        elif self.peso_min:
            return f"+{self.peso_min} kg"
        elif self.peso_max:
            return f"-{self.peso_max} kg"
        return "Sin límite"
    
    def __repr__(self) -> str:
        return f"<Categoria {self.nombre} ({self.federacion.nombre})>"


class MembresiaFederacionDB(Base):
    """Membresía de un alumno a una federación"""
    
    __tablename__ = "membresias_federacion"
    
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"))
    federacion_id = Column(Integer, ForeignKey("federaciones.id", ondelete="CASCADE"))
    
    # Identificación de la membresía
    numero_afiliacion = Column(String, unique=True, index=True, nullable=False)
    
    # Fechas
    fecha_inicio = Column(Date, default=date.today, nullable=False)
    fecha_fin = Column(Date, nullable=True)  # Se calcula con vigencia_dias de la federación
    
    # Finanzas
    costo_pagado = Column(Float, default=0.0)
    
    # Estado
    activa = Column(Boolean, default=True)
    fecha_cancelacion = Column(Date, nullable=True)
    motivo_cancelacion = Column(String, nullable=True)
    
    # Documentación
    certificado_url = Column(String, nullable=True)
    notas = Column(Text, nullable=True)
    
    # Relaciones
    alumno = relationship("AlumnoDB", back_populates="membresias_federacion")
    federacion = relationship("FederacionDB", back_populates="membresias")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-calcular fecha_fin si no se proporciona
        if not self.fecha_fin and hasattr(self, 'federacion') and self.federacion:
            self.fecha_fin = self.fecha_inicio + timedelta(days=self.federacion.vigencia_dias)
    
    @property
    def vigente(self) -> bool:
        if not self.activa:
            return False
        if not self.fecha_fin:
            return True
        return date.today() <= self.fecha_fin
    
    @property
    def dias_restantes(self) -> int:
        if not self.fecha_fin or not self.vigente:
            return 0
        return max(0, (self.fecha_fin - date.today()).days)
    
    @property
    def estado(self) -> str:
        if not self.activa:
            return "Cancelada"
        if not self.vigente:
            return "Vencida"
        if self.dias_restantes < 30:
            return "Por vencer"
        return "Vigente"
    
    def __repr__(self) -> str:
        return f"<Membresia {self.numero_afiliacion} ({self.federacion.nombre})>"