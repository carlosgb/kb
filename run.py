# run.py - Colocar en /home/lenovo/Descargas/kickboxing_manager/run.py
"""Script para ejecutar la aplicación"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor...")
    print("📖 Documentación disponible en http://localhost:8000/docs")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )