# app/main.py
"""Aplicación principal FastAPI"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.core.config import settings
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre de la aplicación"""
    # Inicio: crear tablas
    print("🚀 Iniciando aplicación...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas/verificadas")
    yield
    # Cierre: limpiar recursos si es necesario
    print("👋 Cerrando aplicación...")


# Crear aplicación
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema Profesional de Gestión Deportiva y Acompañamiento Marcial\n\n"
                "## Características\n"
                "- 📋 Gestión completa de alumnos con domicilio y expediente\n"
                "- 👨‍🏫 Administración de maestros y horarios\n"
                "- 🏆 Torneos, eventos y logros\n"
                "- 🏥 Seguro médico y gestión de siniestros\n"
                "- 🌍 Múltiples federaciones (WAKO, IFMA, ISKA)\n"
                "- 📊 Reportes y dashboard\n"
                "- ✅ Asistencias por clase\n"
                "- 💰 Control financiero y pagos",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(api_router)

# Endpoint de health check
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "OK", "version": settings.APP_VERSION}

# Root
@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )