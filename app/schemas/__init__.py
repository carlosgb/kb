# app/schemas/__init__.py
"""Esquemas Pydantic para validación de datos"""

from app.schemas.common import (
    MessageResponse, ErrorResponse, PaginationParams, PaginatedResponse, IdNameResponse
)
from app.schemas.alumno import (
    AlumnoBase, AlumnoCreate, AlumnoUpdate, AlumnoResponse, AlumnoDetailResponse
)
from app.schemas.maestro import (
    MaestroBase, MaestroCreate, MaestroUpdate, MaestroResponse
)
from app.schemas.expediente import (
    ExpedienteBase, ExpedienteUpdate, ExpedienteResponse
)
from app.schemas.federacion import (
    FederacionBase, FederacionCreate, FederacionResponse,
    CategoriaFederacionBase, CategoriaFederacionCreate, CategoriaFederacionResponse,
    MembresiaFederacionBase, MembresiaFederacionCreate, MembresiaFederacionResponse
)
from app.schemas.seguro import (
    AseguradoraBase, AseguradoraCreate, AseguradoraResponse,
    PolizaSeguroBase, PolizaSeguroCreate, PolizaSeguroResponse,
    ContratoSeguroBase, ContratoSeguroCreate, ContratoSeguroResponse,
    SiniestroSeguroBase, SiniestroSeguroCreate, SiniestroSeguroResponse
)
from app.schemas.evento import (
    EventoBase, EventoCreate, EventoUpdate, EventoResponse,
    InscripcionEventoCreate, InscripcionEventoResponse
)
from app.schemas.horario import (
    HorarioClaseBase, HorarioClaseCreate, HorarioClaseUpdate, HorarioClaseResponse,
    InscripcionClaseCreate, InscripcionClaseResponse,
    AsistenciaAlumnoCreate, AsistenciaAlumnoResponse, TomaAsistenciaMasiva
)
from app.schemas.tracking import (
    HistorialPesoCreate, HistorialPesoResponse,
    HistorialGradoCreate, HistorialGradoResponse,
    TecnicaDominadaCreate, TecnicaDominadaResponse,
    LogroCreate, LogroResponse
)

__all__ = [
    # Common
    "MessageResponse", "ErrorResponse", "PaginationParams", "PaginatedResponse", "IdNameResponse",
    # Alumno
    "AlumnoBase", "AlumnoCreate", "AlumnoUpdate", "AlumnoResponse", "AlumnoDetailResponse",
    # Maestro
    "MaestroBase", "MaestroCreate", "MaestroUpdate", "MaestroResponse",
    # Expediente
    "ExpedienteBase", "ExpedienteUpdate", "ExpedienteResponse",
    # Federacion
    "FederacionBase", "FederacionCreate", "FederacionResponse",
    "CategoriaFederacionBase", "CategoriaFederacionCreate", "CategoriaFederacionResponse",
    "MembresiaFederacionBase", "MembresiaFederacionCreate", "MembresiaFederacionResponse",
    # Seguro
    "AseguradoraBase", "AseguradoraCreate", "AseguradoraResponse",
    "PolizaSeguroBase", "PolizaSeguroCreate", "PolizaSeguroResponse",
    "ContratoSeguroBase", "ContratoSeguroCreate", "ContratoSeguroResponse",
    "SiniestroSeguroBase", "SiniestroSeguroCreate", "SiniestroSeguroResponse",
    # Evento
    "EventoBase", "EventoCreate", "EventoUpdate", "EventoResponse",
    "InscripcionEventoCreate", "InscripcionEventoResponse",
    # Horario
    "HorarioClaseBase", "HorarioClaseCreate", "HorarioClaseUpdate", "HorarioClaseResponse",
    "InscripcionClaseCreate", "InscripcionClaseResponse",
    "AsistenciaAlumnoCreate", "AsistenciaAlumnoResponse",
    # Tracking
    "HistorialPesoCreate", "HistorialPesoResponse",
    "HistorialGradoCreate", "HistorialGradoResponse",
    "TecnicaDominadaCreate", "TecnicaDominadaResponse",
    "LogroCreate", "LogroResponse",
]