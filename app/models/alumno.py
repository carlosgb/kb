# app/models/alumno.py
"""Modelo de Alumno (central)"""

from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import date, timedelta
from typing import Optional, List, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.expediente import ExpedienteDB
    from app.models.federacion import MembresiaFederacionDB
    from app.models.seguro import ContratoSeguroDB
    from app.models.evento import InscripcionEventoDB
    from app.models.horario import InscripcionClaseDB, AsistenciaAlumnoDB
    from app.models.tracking import HistorialPesoDB, HistorialGradoDB, TecnicaDominadaDB, LogroDB

class AlumnoDB(Base):
    """Modelo principal del alumno con todos sus datos personales"""
    
    __tablename__ = "alumnos"
    
    # === IDENTIFICACIÓN ===
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    sexo = Column(String, nullable=False)  # "M", "F", "Otro"
    fecha_nacimiento = Column(Date, nullable=False)
    
    # === CONTACTO PERSONAL ===
    email = Column(String, unique=True, index=True, nullable=True)
    telefono_celular = Column(String, nullable=False)
    telefono_casa = Column(String, nullable=True)
    
    # === DOMICILIO COMPLETO ===
    calle = Column(String, nullable=False)
    numero = Column(String, nullable=True)
    colonia = Column(String, nullable=True)
    ciudad = Column(String, default="Ciudad de México")
    codigo_postal = Column(String, nullable=True)
    
    # === DATOS FÍSICOS ===
    altura = Column(Float, nullable=False)  # en metros
    peso_actual = Column(Float, nullable=False)  # en kg
    
    # === DATOS DEPORTIVOS ===
    grado_actual = Column(String, default="Principiante")
    es_competidor = Column(Boolean, default=False)
    
    # === DATOS ESCOLARES (para menores) ===
    escuela = Column(String, nullable=True)
    grado_escolar = Column(String, nullable=True)
    
    # === CONTROL DE ASISTENCIA ===
    asistencias_totales = Column(Integer, default=0)
    
    # === CONTROL DE PAGOS ===
    fecha_ultimo_pago = Column(Date, default=date.today)
    monto_mensualidad = Column(Float, default=500.0)
    
    # === METADATA ===
    activo = Column(Boolean, default=True)
    fecha_registro = Column(Date, default=date.today)
    notas = Column(String, nullable=True)
    
    # === RELACIONES ===
    expediente = relationship("ExpedienteDB", back_populates="alumno", uselist=False, cascade="all, delete-orphan")
    membresias_federacion = relationship("MembresiaFederacionDB", back_populates="alumno", cascade="all, delete-orphan")
    seguros = relationship("ContratoSeguroDB", back_populates="alumno", cascade="all, delete-orphan")
    inscripciones_eventos = relationship("InscripcionEventoDB", back_populates="alumno", cascade="all, delete-orphan")
    inscripciones_clase = relationship("InscripcionClaseDB", back_populates="alumno", cascade="all, delete-orphan")
    asistencias = relationship("AsistenciaAlumnoDB", back_populates="alumno", cascade="all, delete-orphan")
    pesos = relationship("HistorialPesoDB", back_populates="alumno", cascade="all, delete-orphan")
    grados = relationship("HistorialGradoDB", back_populates="alumno", cascade="all, delete-orphan")
    tecnicas = relationship("TecnicaDominadaDB", back_populates="alumno", cascade="all, delete-orphan")
    logros = relationship("LogroDB", back_populates="alumno", cascade="all, delete-orphan")
    
    # === PROPIEDADES CALCULADAS ===
    
    @property
    def edad(self) -> int:
        """Calcula la edad actual del alumno"""
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    @property
    def nombre_completo(self) -> str:
        """Nombre completo del alumno"""
        return f"{self.nombre} {self.apellidos}"
    
    @property
    def imc(self) -> float:
        """Índice de Masa Corporal"""
        try:
            if self.peso_actual and self.altura > 0:
                resultado = self.peso_actual / (self.altura ** 2)
                return round(resultado, 2)
            return 0.0
        except (TypeError, ZeroDivisionError):
            return 0.0
    
    @property
    def monto_con_recargo(self) -> float:
        """Calcula el 10% de recargo si el pago tiene más de 30 días de retraso"""
        from app.core.config import settings
        hoy = date.today()
        dias_atraso = (hoy - self.fecha_ultimo_pago).days - settings.DIAS_RETRASO_PAGO_RECARGO
        if dias_atraso > 0:
            return round(self.monto_mensualidad * (1 + settings.PORCENTAJE_RECARGO / 100), 2)
        return self.monto_mensualidad
    
    @property
    def estado_pago(self) -> str:
        """Estado del pago de mensualidad"""
        from app.core.config import settings
        hoy = date.today()
        dias = (hoy - self.fecha_ultimo_pago).days
        if dias > settings.DIAS_RETRASO_PAGO_RECARGO:
            return "Vencido"
        elif dias > 0:
            return "Por vencer"
        return "Al corriente"
    
    @property
    def membresia_activa(self):
        """Obtiene la membresía federativa activa más reciente"""
        activas = [m for m in self.membresias_federacion if m.vigente]
        if not activas:
            return None
        return max(activas, key=lambda m: m.fecha_inicio)
    
    @property
    def seguro_activo(self):
        """Obtiene el seguro activo del alumno"""
        activos = [s for s in self.seguros if s.vigente]
        if not activos:
            return None
        return max(activos, key=lambda s: s.fecha_inicio)
    
    @property
    def tiene_seguro_vigente(self) -> bool:
        return self.seguro_activo is not None
    
    @property
    def categoria_wako(self) -> str:
        """Compatibilidad con código existente: calcula categoría según WAKO"""
        # Si tiene membresía WAKO activa, usa esa, si no calcula genérica
        if self.membresia_activa and self.membresia_activa.federacion.nombre == "WAKO":
            return self.categoria_actual
        return self.categoria_generica
    
    @property
    def categoria_generica(self) -> str:
        """Categoría genérica basada en edad y peso"""
        if self.edad < 10:
            division = "Children"
        elif 10 <= self.edad <= 12:
            division = "Younger Cadet"
        elif 13 <= self.edad <= 15:
            division = "Older Cadet"
        elif 16 <= self.edad <= 18:
            division = "Junior"
        else:
            division = "Senior"
        return f"{division} | {self.peso_actual}kg"
    
    @property
    def categoria_actual(self) -> str:
        """Calcula categoría según la federación activa del alumno"""
        membresia = self.membresia_activa
        if not membresia:
            return self.categoria_generica
        
        # Buscar categoría que coincida con edad y peso
        for cat in membresia.federacion.categorias:
            if not cat.activo:
                continue
            if cat.genero and cat.genero != self.sexo:
                continue
            if cat.edad_min and self.edad < cat.edad_min:
                continue
            if cat.edad_max and self.edad > cat.edad_max:
                continue
            if cat.peso_min and self.peso_actual < cat.peso_min:
                continue
            if cat.peso_max and self.peso_actual > cat.peso_max:
                continue
            return f"{cat.nombre} ({membresia.federacion.nombre})"
        
        return f"Sin categoría asignada ({membresia.federacion.nombre})"
    
    @property
    def resumen_seguro(self) -> dict:
        """Resumen del seguro activo"""
        seguro = self.seguro_activo
        if not seguro:
            return {"estado": "Sin seguro vigente"}
        
        return {
            "estado": "Vigente" if seguro.vigente else "Vencido",
            "aseguradora": seguro.poliza.aseguradora.nombre,
            "plan": seguro.poliza.nombre_plan,
            "numero_certificado": seguro.numero_certificado,
            "vigencia_hasta": seguro.fecha_fin,
            "dias_restantes": seguro.dias_restantes,
            "cobertura_maxima": seguro.poliza.cobertura_medica_max,
            "deducible": seguro.poliza.deducible
        }
    
    def __repr__(self) -> str:
        return f"<Alumno {self.nombre_completo} (ID: {self.id})>"