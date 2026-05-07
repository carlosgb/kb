# app/core/config.py
"""Configuración de la aplicación usando variables de entorno"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuración centralizada"""
    
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./kickboxing.db")
    
    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Aplicación
    APP_NAME: str = "WAKO School Manager Pro"
    APP_VERSION: str = "4.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Reglas de negocio
    VIGENCIA_CERTIFICADO_MEDICO_DIAS: int = 365
    DIAS_RETRASO_PAGO_RECARGO: int = 30
    PORCENTAJE_RECARGO: float = 10.0  # 10% de recargo
    
    # Archivos
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE_MB: int = 10
    
    def __init__(self):
        # Crear directorio de uploads si no existe
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

settings = Settings()