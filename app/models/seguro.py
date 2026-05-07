# app/models/seguro.py
"""Modelos para gestión de seguros médicos"""

from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import date
from typing import Optional, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from .alumno import AlumnoDB


class AseguradoraDB(Base):
    """Compañía aseguradora"""
    
    __tablename__ = "aseguradoras"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    razon_social = Column(String, nullable=True)
    rfc = Column(String, unique=True, nullable=True)
    
    # Contacto
    telefono_contacto = Column(String, nullable=True)
    email_contacto = Column(String, nullable=True)
    sitio_web = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    
    # Configuración comercial
    activo = Column(Boolean, default=True)
    comision_porcentaje = Column(Float, default=0.0)  # Comisión para la escuela
    
    # Metadata
    logo_url = Column(String, nullable=True)
    notas = Column(Text, nullable=True)
    
    # Relaciones
    polizas = relationship("PolizaSeguroDB", back_populates="aseguradora", cascade="all, delete-orphan")
    
    @property
    def polizas_activas(self):
        return [p for p in self.polizas if p.activa]
    
    def __repr__(self) -> str:
        return f"<Aseguradora {self.nombre}>"


class PolizaSeguroDB(Base):
    """Póliza de seguro (plan maestro)"""
    
    __tablename__ = "polizas_seguro"
    
    id = Column(Integer, primary_key=True, index=True)
    aseguradora_id = Column(Integer, ForeignKey("aseguradoras.id", ondelete="CASCADE"))
    
    # Identificación
    numero_poliza = Column(String, nullable=False, index=True)
    nombre_plan = Column(String, nullable=False)  # "Deportista Elite", "Básico"
    
    # Coberturas
    cobertura_medica_max = Column(Float, default=50000.0)
    cobertura_incapacidad = Column(Float, default=0.0)
    cobertura_muerte = Column(Float, default=100000.0)
    cobertura_dental = Column(Float, default=0.0)
    cobertura_ambulancia = Column(Float, default=0.0)
    
    # Costos para el alumno
    deducible = Column(Float, default=0.0)
    copago_porcentaje = Column(Float, default=0.0)
    
    # Exclusiones y condiciones
    exclusiones = Column(Text, nullable=True)
    condiciones_especiales = Column(Text, nullable=True)
    
    # Vigencia de la póliza (fechas en que el contrato maestro está activo)
    fecha_inicio_vigencia = Column(Date, nullable=False)
    fecha_fin_vigencia = Column(Date, nullable=False)
    
    # Costo para la escuela
    costo_mensual_por_alumno = Column(Float, default=0.0)
    costo_anual_por_alumno = Column(Float, default=0.0)
    
    # Estado
    activa = Column(Boolean, default=True)
    
    # Relaciones
    aseguradora = relationship("AseguradoraDB", back_populates="polizas")
    contratos = relationship("ContratoSeguroDB", back_populates="poliza", cascade="all, delete-orphan")
    
    @property
    def vigente(self) -> bool:
        hoy = date.today()
        return (self.fecha_inicio_vigencia <= hoy <= self.fecha_fin_vigencia) and self.activa
    
    def __repr__(self) -> str:
        return f"<Poliza {self.numero_poliza} - {self.nombre_plan}>"


class ContratoSeguroDB(Base):
    """Contrato de seguro individual por alumno"""
    
    __tablename__ = "contratos_seguro"
    
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"))
    poliza_id = Column(Integer, ForeignKey("polizas_seguro.id", ondelete="CASCADE"))
    
    # Identificación individual
    numero_certificado = Column(String, unique=True, index=True, nullable=False)
    
    # Fechas de vigencia individual
    fecha_inicio = Column(Date, default=date.today, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    
    # Prima pagada
    prima_pagada = Column(Float, default=0.0)
    forma_pago = Column(String, default="Anual")  # "Mensual", "Trimestral", "Anual", "Incluido"
    
    # Estado
    activo = Column(Boolean, default=True)
    fecha_cancelacion = Column(Date, nullable=True)
    motivo_cancelacion = Column(String, nullable=True)
    
    # Documentación
    poliza_pdf_url = Column(String, nullable=True)
    notas = Column(Text, nullable=True)
    
    # Relaciones
    alumno = relationship("AlumnoDB", back_populates="seguros")
    poliza = relationship("PolizaSeguroDB", back_populates="contratos")
    siniestros = relationship("SiniestroSeguroDB", back_populates="contrato", cascade="all, delete-orphan")
    
    @property
    def vigente(self) -> bool:
        if not self.activo:
            return False
        hoy = date.today()
        return self.fecha_inicio <= hoy <= self.fecha_fin
    
    @property
    def dias_restantes(self) -> int:
        if not self.vigente or not self.fecha_fin:
            return 0
        return max(0, (self.fecha_fin - date.today()).days)
    
    @property
    def cobertura_resumida(self) -> dict:
        return {
            "aseguradora": self.poliza.aseguradora.nombre,
            "plan": self.poliza.nombre_plan,
            "cobertura_maxima": self.poliza.cobertura_medica_max,
            "deducible": self.poliza.deducible,
            "vigencia_hasta": self.fecha_fin
        }
    
    def __repr__(self) -> str:
        return f"<ContratoSeguro {self.numero_certificado}>"


class SiniestroSeguroDB(Base):
    """Reclamo o siniestro reportado al seguro"""
    
    __tablename__ = "siniestros_seguro"
    
    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey("contratos_seguro.id", ondelete="CASCADE"))
    
    # Datos del accidente
    fecha_accidente = Column(Date, nullable=False)
    descripcion = Column(Text, nullable=False)
    lugar_accidente = Column(String, nullable=True)  # "Gimnasio", "Torneo", "Entrenamiento"
    parte_del_cuerpo = Column(String, nullable=True)  # "Rodilla", "Nariz", "Muñeca"
    diagnostico = Column(String, nullable=True)
    
    # Gastos
    gastos_totales = Column(Float, default=0.0)
    monto_cubierto = Column(Float, default=0.0)
    monto_deducible = Column(Float, default=0.0)
    monto_no_cubierto = Column(Float, default=0.0)
    
    # Estado del siniestro
    estado = Column(String, default="Reportado")  # "Reportado", "En proceso", "Aprobado", "Rechazado", "Pagado"
    numero_siniestro = Column(String, unique=True, index=True, nullable=False)
    
    # Fechas de proceso
    fecha_reporte = Column(Date, default=date.today)
    fecha_resolucion = Column(Date, nullable=True)
    fecha_pago = Column(Date, nullable=True)
    
    # Documentación
    dictamen_medico_url = Column(String, nullable=True)
    facturas_url = Column(Text, nullable=True)  # JSON con URLs de facturas
    notas = Column(Text, nullable=True)
    
    # Relaciones
    contrato = relationship("ContratoSeguroDB", back_populates="siniestros")
    
    def __repr__(self) -> str:
        return f"<Siniestro {self.numero_siniestro} - {self.estado}>"