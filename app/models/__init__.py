# app/models/__init__.py
"""Todos los modelos de la aplicación"""

# Importar directamente cada modelo para que estén disponibles
from app.models.alumno import AlumnoDB
from app.models.maestro import MaestroDB
from app.models.federacion import FederacionDB, MembresiaFederacionDB, CategoriaFederacionDB
from app.models.seguro import AseguradoraDB, PolizaSeguroDB, ContratoSeguroDB, SiniestroSeguroDB
from app.models.evento import EventoDB, InscripcionEventoDB
from app.models.horario import HorarioClaseDB, InscripcionClaseDB, AsistenciaAlumnoDB, AsistenciaMaestroDB
from app.models.expediente import ExpedienteDB
from app.models.tracking import HistorialPesoDB, HistorialGradoDB, TecnicaDominadaDB, LogroDB

__all__ = [
    "AlumnoDB",
    "MaestroDB",
    "FederacionDB",
    "MembresiaFederacionDB",
    "CategoriaFederacionDB",
    "AseguradoraDB",
    "PolizaSeguroDB",
    "ContratoSeguroDB",
    "SiniestroSeguroDB",
    "EventoDB",
    "InscripcionEventoDB",
    "HorarioClaseDB",
    "InscripcionClaseDB",
    "AsistenciaAlumnoDB",
    "AsistenciaMaestroDB",
    "ExpedienteDB",
    "HistorialPesoDB",
    "HistorialGradoDB",
    "TecnicaDominadaDB",
    "LogroDB",
]