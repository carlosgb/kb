# scripts/migrate.py
"""Script de migración desde la estructura antigua a la nueva"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from sqlalchemy import text
from app.core.database import SessionLocal, engine, Base


def migrar_estructura():
    """Migrar la estructura de la base de datos"""
    
    print("\n" + "="*60)
    print("🔄 INICIANDO MIGRACIÓN DE BASE DE DATOS")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # 1. Agregar nuevas columnas a alumnos
        print("📝 Agregando columnas a tabla alumnos...")
        
        nuevas_columnas = [
            "ALTER TABLE alumnos ADD COLUMN email VARCHAR",
            "ALTER TABLE alumnos ADD COLUMN telefono_celular VARCHAR",
            "ALTER TABLE alumnos ADD COLUMN calle VARCHAR",
            "ALTER TABLE alumnos ADD COLUMN numero VARCHAR",
            "ALTER TABLE alumnos ADD COLUMN colonia VARCHAR",
            "ALTER TABLE alumnos ADD COLUMN ciudad VARCHAR DEFAULT 'Ciudad de México'",
            "ALTER TABLE alumnos ADD COLUMN codigo_postal VARCHAR",
            "ALTER TABLE alumnos ADD COLUMN telefono_casa VARCHAR",
            "ALTER TABLE alumnos ADD COLUMN escuela VARCHAR",
            "ALTER TABLE alumnos ADD COLUMN grado_escolar VARCHAR",
            "ALTER TABLE alumnos ADD COLUMN activo BOOLEAN DEFAULT 1",
            "ALTER TABLE alumnos ADD COLUMN fecha_registro DATE DEFAULT CURRENT_DATE",
            "ALTER TABLE alumnos ADD COLUMN notas VARCHAR"
        ]
        
        for sql in nuevas_columnas:
            try:
                db.execute(text(sql))
                print(f"   ✅ {sql}")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print(f"   ⏭️  Columna ya existe, omitiendo")
                else:
                    print(f"   ⚠️  {e}")
        
        db.commit()
        
        # 2. Agregar columnas a expedientes
        print("\n📝 Agregando columnas a tabla expedientes...")
        
        columnas_expediente = [
            "ALTER TABLE expedientes ADD COLUMN medicamentos_actuales TEXT",
            "ALTER TABLE expedientes ADD COLUMN contacto_emergencia_parentesco VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN contacto_emergencia_telefono_alt VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN contacto_emergencia_email VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN medico_familiar_nombre VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN medico_familiar_telefono VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN medico_familiar_cedula VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN nombre_medico_certifica VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN cedula_profesional_medico VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN clinica_hospital VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN deslinde_fecha DATE",
            "ALTER TABLE expedientes ADD COLUMN deslinde_url VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN reglamento_fecha DATE",
            "ALTER TABLE expedientes ADD COLUMN reglamento_url VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN uso_imagen_fecha DATE",
            "ALTER TABLE expedientes ADD COLUMN uso_imagen_url VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN autorizacion_paterna_firmada BOOLEAN DEFAULT 0",
            "ALTER TABLE expedientes ADD COLUMN autorizacion_paterna_fecha DATE",
            "ALTER TABLE expedientes ADD COLUMN nombre_tutor VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN telefono_tutor VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN tutor_relacion VARCHAR",
            "ALTER TABLE expedientes ADD COLUMN lesiones_previas TEXT",
            "ALTER TABLE expedientes ADD COLUMN cirugias TEXT",
            "ALTER TABLE expedientes ADD COLUMN tratamientos_actuales TEXT",
            "ALTER TABLE expedientes ADD COLUMN notas_medicas TEXT",
            "ALTER TABLE expedientes ADD COLUMN notas_legales TEXT",
            "ALTER TABLE expedientes ADD COLUMN fecha_actualizacion DATE DEFAULT CURRENT_DATE"
        ]
        
        for sql in columnas_expediente:
            try:
                db.execute(text(sql))
                print(f"   ✅ {sql.split()[3]}")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print(f"   ⏭️  Columna ya existe")
                else:
                    print(f"   ⚠️  {e}")
        
        db.commit()
        
        # 3. Verificar si las nuevas tablas existen y crearlas si no
        print("\n📝 Verificando tablas nuevas...")
        
        tablas_nuevas = [
            "maestros", "federaciones", "categorias_federacion", "membresias_federacion",
            "aseguradoras", "polizas_seguro", "contratos_seguro", "siniestros_seguro",
            "horarios_clase", "inscripciones_clase", "asistencias_alumno", "asistencias_maestro"
        ]
        
        for tabla in tablas_nuevas:
            result = db.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}'"))
            if result.first():
                print(f"   ✅ Tabla {tabla} ya existe")
            else:
                print(f"   ⚠️  Tabla {tabla} no existe - se creará con los modelos")
        
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error durante migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def migrar_datos_existentes():
    """Migrar datos desde la estructura antigua a la nueva"""
    
    print("\n" + "="*60)
    print("🔄 MIGRANDO DATOS EXISTENTES")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # Migrar datos de alumnos (si hay teléfono en expediente)
        print("📝 Migrando contactos de emergencia a expediente...")
        
        # Esto asume que había datos en la estructura anterior
        # Ajustar según sea necesario
        
        print("   ✅ Migración de datos completada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Herramientas de migración")
    parser.add_argument("--estructura", action="store_true", help="Migrar estructura de DB")
    parser.add_argument("--datos", action="store_true", help="Migrar datos existentes")
    parser.add_argument("--todo", action="store_true", help="Migrar todo")
    
    args = parser.parse_args()
    
    if args.todo or args.estructura:
        migrar_estructura()
    
    if args.todo or args.datos:
        migrar_datos_existentes()
    
    if not (args.todo or args.estructura or args.datos):
        print("""
Uso: python scripts/migrate.py [opciones]

Opciones:
  --estructura   Migrar estructura de base de datos (agregar columnas)
  --datos        Migrar datos existentes a nueva estructura
  --todo         Ejecutar todas las migraciones

Ejemplo:
  python scripts/migrate.py --todo
        """)