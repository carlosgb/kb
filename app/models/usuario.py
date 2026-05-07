# app/models/usuario.py
"""Modelo de Usuario para autenticación"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Roles: admin, maestro, recepcion, caja, invitado
    rol = Column(String(20), nullable=False, default="invitado")
    
    # Datos personales
    nombre = Column(String(50), nullable=False)
    apellidos = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    
    # Estado
    activo = Column(Boolean, default=True)
    ultimo_acceso = Column(DateTime, nullable=True)
    
    # Relaciones con modelos existentes (opcional)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=True)
    maestro_id = Column(Integer, ForeignKey("maestros.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    alumno = relationship("AlumnoDB", foreign_keys=[alumno_id])
    maestro = relationship("MaestroDB", foreign_keys=[maestro_id])
    
    def __repr__(self):
        return f"<Usuario {self.username} ({self.rol})>"