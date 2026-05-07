# app/api/router.py
"""Router principal de la API"""

from fastapi import APIRouter

from .v1 import (
    alumnos, maestros, federaciones, seguros, 
    eventos, horarios, asistencias, reportes, dashboard, auth
)

api_router = APIRouter(prefix="/api/v1")

# Registrar todos los routers
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(alumnos.router, prefix="/alumnos", tags=["Alumnos"])
api_router.include_router(maestros.router, prefix="/maestros", tags=["Maestros"])
api_router.include_router(federaciones.router, prefix="/federaciones", tags=["Federaciones"])
api_router.include_router(seguros.router, prefix="/seguros", tags=["Seguros"])
api_router.include_router(eventos.router, prefix="/eventos", tags=["Eventos"])
api_router.include_router(horarios.router, prefix="/horarios", tags=["Horarios"])
api_router.include_router(asistencias.router, prefix="/asistencias", tags=["Asistencias"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])