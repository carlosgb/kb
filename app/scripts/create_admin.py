# scripts/create_admin.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.usuario import UsuarioDB
from app.core.auth import get_password_hash

db = SessionLocal()

# Verificar si ya existe admin
admin = db.query(UsuarioDB).filter(UsuarioDB.username == "admin").first()
if not admin:
    admin = UsuarioDB(
        username="admin",
        email="admin@wako.com",
        hashed_password=get_password_hash("admin123"),
        nombre="Administrador",
        apellidos="Sistema",
        rol="admin",
        activo=True
    )
    db.add(admin)
    db.commit()
    print("✅ Usuario administrador creado: admin / admin123")
else:
    print("ℹ️ El usuario administrador ya existe")

db.close()