# scripts/seed_data.py
"""Datos iniciales para poblar la base de datos"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from app.core.database import SessionLocal, engine, Base
from app.models import (
    FederacionDB, CategoriaFederacionDB,
    AseguradoraDB, PolizaSeguroDB,
    MaestroDB, HorarioClaseDB
)


def seed_federaciones(db):
    """Cargar federaciones iniciales"""
    print("📋 Cargando federaciones...")
    
    federaciones = [
        {
            "nombre": "WAKO",
            "nombre_completo": "World Association of Kickboxing Organizations",
            "pais_origen": "Hungría",
            "vigencia_dias": 365,
            "sitio_web": "https://www.wakoweb.com"
        },
        {
            "nombre": "IFMA",
            "nombre_completo": "International Federation of Muaythai Associations",
            "pais_origen": "Tailandia",
            "vigencia_dias": 365,
            "sitio_web": "https://www.ifmamuaythai.org"
        },
        {
            "nombre": "ISKA",
            "nombre_completo": "International Sport Kickboxing Association",
            "pais_origen": "USA",
            "vigencia_dias": 365,
            "sitio_web": "https://www.iska.com"
        }
    ]
    
    for fed_data in federaciones:
        fed = FederacionDB(**fed_data)
        db.add(fed)
    
    db.commit()
    print(f"   ✅ {len(federaciones)} federaciones cargadas")
    
    # Categorías para WAKO
    wako = db.query(FederacionDB).filter_by(nombre="WAKO").first()
    if wako:
        categorias = [
            {"nombre": "Children (8-9 años)", "edad_min": 8, "edad_max": 9},
            {"nombre": "Younger Cadet (10-12 años)", "edad_min": 10, "edad_max": 12},
            {"nombre": "Older Cadet (13-15 años)", "edad_min": 13, "edad_max": 15},
            {"nombre": "Junior (16-18 años)", "edad_min": 16, "edad_max": 18},
            {"nombre": "Senior (+18 años)", "edad_min": 18},
            {"nombre": "Master (+35 años)", "edad_min": 35},
        ]
        
        for cat_data in categorias:
            cat = CategoriaFederacionDB(federacion_id=wako.id, **cat_data)
            db.add(cat)
        
        db.commit()
        print(f"   ✅ {len(categorias)} categorías para WAKO")


def seed_aseguradoras(db):
    """Cargar aseguradoras y pólizas iniciales"""
    print("🏥 Cargando aseguradoras...")
    
    aseguradoras = [
        {
            "nombre": "GNP Seguros",
            "razon_social": "Grupo Nacional Provincial S.A.B.",
            "rfc": "GNP800101XXX",
            "telefono_contacto": "800-123-4567",
            "sitio_web": "https://www.gnp.com.mx"
        },
        {
            "nombre": "AXA",
            "razon_social": "AXA Seguros S.A. de C.V.",
            "rfc": "AXA850101XXX",
            "telefono_contacto": "800-234-5678",
            "sitio_web": "https://www.axa.mx"
        }
    ]
    
    for data in aseguradoras:
        aseguradora = AseguradoraDB(**data)
        db.add(aseguradora)
    
    db.commit()
    
    # Pólizas para GNP
    gnp = db.query(AseguradoraDB).filter_by(nombre="GNP Seguros").first()
    if gnp:
        polizas = [
            {
                "aseguradora_id": gnp.id,
                "numero_poliza": "POL-GNP-2024-001",
                "nombre_plan": "Deportista Élite",
                "cobertura_medica_max": 150000.0,
                "cobertura_incapacidad": 50000.0,
                "cobertura_muerte": 250000.0,
                "cobertura_dental": 10000.0,
                "deducible": 1500.0,
                "copago_porcentaje": 10.0,
                "fecha_inicio_vigencia": date(2024, 1, 1),
                "fecha_fin_vigencia": date(2025, 12, 31),
                "costo_mensual_por_alumno": 250.0,
            },
            {
                "aseguradora_id": gnp.id,
                "numero_poliza": "POL-GNP-2024-002",
                "nombre_plan": "Básico",
                "cobertura_medica_max": 50000.0,
                "cobertura_muerte": 100000.0,
                "cobertura_dental": 5000.0,
                "deducible": 2000.0,
                "copago_porcentaje": 20.0,
                "fecha_inicio_vigencia": date(2024, 1, 1),
                "fecha_fin_vigencia": date(2025, 12, 31),
                "costo_mensual_por_alumno": 120.0,
            }
        ]
        
        for pol_data in polizas:
            poliza = PolizaSeguroDB(**pol_data)
            db.add(poliza)
        
        db.commit()
        print(f"   ✅ {len(polizas)} pólizas para GNP")


def seed_maestros_ejemplo(db):
    """Cargar maestros de ejemplo"""
    print("👨‍🏫 Cargando maestros de ejemplo...")
    
    maestros = [
        {
            "nombre": "Carlos",
            "apellidos": "Rodríguez",
            "email": "carlos.rodriguez@kickboxing.com",
            "telefono": "555-123-4567",
            "especialidad": "K1",
            "grado": "Cinturón Negro 3er Dan",
            "anos_experiencia": 15,
            "fecha_contratacion": date(2020, 1, 15),
            "sueldo_base": 8000.0,
            "activo": True
        },
        {
            "nombre": "Ana",
            "apellidos": "Martínez",
            "email": "ana.martinez@kickboxing.com",
            "telefono": "555-234-5678",
            "especialidad": "Point Fighting",
            "grado": "Cinturón Negro 2do Dan",
            "anos_experiencia": 10,
            "fecha_contratacion": date(2021, 3, 10),
            "sueldo_base": 7000.0,
            "activo": True
        },
        {
            "nombre": "Luis",
            "apellidos": "Hernández",
            "email": "luis.hernandez@kickboxing.com",
            "telefono": "555-345-6789",
            "especialidad": "Kick Light",
            "grado": "Cinturón Negro 1er Dan",
            "anos_experiencia": 8,
            "fecha_contratacion": date(2022, 6, 20),
            "sueldo_base": 6000.0,
            "activo": True
        }
    ]
    
    for data in maestros:
        maestro = MaestroDB(**data)
        db.add(maestro)
    
    db.commit()
    print(f"   ✅ {len(maestros)} maestros cargados")
    
    # Crear horarios para los maestros
    carlos = db.query(MaestroDB).filter_by(email="carlos.rodriguez@kickboxing.com").first()
    ana = db.query(MaestroDB).filter_by(email="ana.martinez@kickboxing.com").first()
    luis = db.query(MaestroDB).filter_by(email="luis.hernandez@kickboxing.com").first()
    
    if carlos:
        horarios = [
            {
                "nombre": "K1 Avanzados",
                "tipo_clase": "K1",
                "nivel": "Avanzados",
                "dia_semana": 0,  # Lunes
                "hora_inicio": "18:00",
                "hora_fin": "19:30",
                "duracion_minutos": 90,
                "capacidad_maxima": 15,
                "maestro_id": carlos.id,
                "activo": True
            },
            {
                "nombre": "K1 Intermedios",
                "tipo_clase": "K1",
                "nivel": "Intermedios",
                "dia_semana": 2,  # Miércoles
                "hora_inicio": "18:00",
                "hora_fin": "19:30",
                "duracion_minutos": 90,
                "capacidad_maxima": 20,
                "maestro_id": carlos.id,
                "activo": True
            }
        ]
        
        for h_data in horarios:
            horario = HorarioClaseDB(**h_data)
            db.add(horario)
    
    if ana:
        horarios = [
            {
                "nombre": "Point Fighting Competidores",
                "tipo_clase": "Point Fighting",
                "nivel": "Avanzados",
                "dia_semana": 1,  # Martes
                "hora_inicio": "17:00",
                "hora_fin": "18:30",
                "duracion_minutos": 90,
                "capacidad_maxima": 15,
                "maestro_id": ana.id,
                "activo": True
            }
        ]
        
        for h_data in horarios:
            horario = HorarioClaseDB(**h_data)
            db.add(horario)
    
    if luis:
        horarios = [
            {
                "nombre": "Kick Light Principiantes",
                "tipo_clase": "Kick Light",
                "nivel": "Principiantes",
                "dia_semana": 3,  # Jueves
                "hora_inicio": "19:00",
                "hora_fin": "20:30",
                "duracion_minutos": 90,
                "capacidad_maxima": 25,
                "maestro_id": luis.id,
                "activo": True
            },
            {
                "nombre": "Infantil (8-12 años)",
                "tipo_clase": "Infantil",
                "nivel": "Mixto",
                "dia_semana": 4,  # Viernes
                "hora_inicio": "16:00",
                "hora_fin": "17:30",
                "duracion_minutos": 90,
                "capacidad_maxima": 20,
                "maestro_id": luis.id,
                "activo": True
            }
        ]
        
        for h_data in horarios:
            horario = HorarioClaseDB(**h_data)
            db.add(horario)
    
    db.commit()
    print(f"   ✅ Horarios creados")


def main():
    """Ejecutar todos los seeds"""
    print("\n" + "="*50)
    print("🌱 INICIANDO SEED DE DATOS")
    print("="*50 + "\n")
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        seed_federaciones(db)
        seed_aseguradoras(db)
        seed_maestros_ejemplo(db)
        
        print("\n" + "="*50)
        print("✅ SEED COMPLETADO EXITOSAMENTE")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error durante seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()