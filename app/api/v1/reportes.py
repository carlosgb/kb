# app/api/v1/reportes.py
"""Endpoints para reportes y análisis"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta
from calendar import monthrange

from app.core.database import get_db
from app.models import (
    AlumnoDB, EventoDB, HorarioClaseDB, AsistenciaAlumnoDB,
    ContratoSeguroDB, MembresiaFederacionDB
)

router = APIRouter()


# ==================== REPORTES FINANCIEROS ====================

@router.get("/financiero/ingresos-mensuales", response_model=dict)
def ingresos_mensuales(
    anio: int,
    mes: int,
    db: Session = Depends(get_db)
):
    """Reporte de ingresos mensuales (mensualidades + eventos + seguros)"""
    
    # Calcular rango del mes
    _, ultimo_dia = monthrange(anio, mes)
    fecha_inicio = date(anio, mes, 1)
    fecha_fin = date(anio, mes, ultimo_dia)
    
    # Ingresos por mensualidades (alumnos que pagaron en este mes)
    alumnos_pagaron = db.query(AlumnoDB).filter(
        AlumnoDB.fecha_ultimo_pago >= fecha_inicio,
        AlumnoDB.fecha_ultimo_pago <= fecha_fin
    ).count()
    
    ingresos_mensualidades = alumnos_pagaron * 500  # Monto promedio
    
    # Ingresos por eventos en este mes
    eventos_mes = db.query(EventoDB).filter(
        EventoDB.fecha >= fecha_inicio,
        EventoDB.fecha <= fecha_fin
    ).all()
    
    ingresos_eventos = sum(e.ingresos_estimados for e in eventos_mes)
    
    # Ingresos por seguros contratados en el mes
    seguros_mes = db.query(ContratoSeguroDB).filter(
        ContratoSeguroDB.fecha_inicio >= fecha_inicio,
        ContratoSeguroDB.fecha_inicio <= fecha_fin
    ).all()
    
    ingresos_seguros = sum(s.prima_pagada for s in seguros_mes)
    
    # Ingresos por membresías federativas
    membresias_mes = db.query(MembresiaFederacionDB).filter(
        MembresiaFederacionDB.fecha_inicio >= fecha_inicio,
        MembresiaFederacionDB.fecha_inicio <= fecha_fin
    ).all()
    
    ingresos_membresias = sum(m.costo_pagado for m in membresias_mes)
    
    total = ingresos_mensualidades + ingresos_eventos + ingresos_seguros + ingresos_membresias
    
    return {
        "periodo": {"anio": anio, "mes": mes},
        "detalle": {
            "mensualidades": ingresos_mensualidades,
            "eventos": ingresos_eventos,
            "seguros": ingresos_seguros,
            "membresias_federativas": ingresos_membresias
        },
        "total": total
    }


@router.get("/financiero/adeudos", response_model=List[dict])
def alumnos_con_adeudo(
    dias_mora: int = Query(30, ge=1, le=180),
    db: Session = Depends(get_db)
):
    """Lista de alumnos con pagos vencidos"""
    
    fecha_limite = date.today() - timedelta(days=dias_mora)
    
    alumnos = db.query(AlumnoDB).filter(
        AlumnoDB.activo == True,
        AlumnoDB.fecha_ultimo_pago <= fecha_limite
    ).all()
    
    return [
        {
            "id": a.id,
            "nombre": a.nombre_completo,
            "telefono": a.telefono_celular,
            "ultimo_pago": a.fecha_ultimo_pago,
            "dias_atraso": (date.today() - a.fecha_ultimo_pago).days,
            "adeudo_estimado": a.monto_con_recargo
        }
        for a in alumnos
    ]


# ==================== REPORTES DE ASISTENCIA ====================

@router.get("/asistencia/alumnos-inactivos", response_model=List[dict])
def alumnos_inactivos(
    dias_sin_asistencia: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Alumnos que no han asistido en los últimos X días"""
    
    fecha_limite = date.today() - timedelta(days=dias_sin_asistencia)
    
    # Obtener alumnos que asistieron después de la fecha límite
    alumnos_activos = db.query(AsistenciaAlumnoDB.alumno_id).filter(
        AsistenciaAlumnoDB.fecha_clase >= fecha_limite
    ).distinct().all()
    
    alumnos_activos_ids = [a[0] for a in alumnos_activos]
    
    # Alumnos activos que no están en la lista
    alumnos = db.query(AlumnoDB).filter(
        AlumnoDB.activo == True,
        AlumnoDB.id.notin_(alumnos_activos_ids) if alumnos_activos_ids else True
    ).all()
    
    return [
        {
            "id": a.id,
            "nombre": a.nombre_completo,
            "telefono": a.telefono_celular,
            "ultima_asistencia": db.query(AsistenciaAlumnoDB.fecha_clase)
                .filter(AsistenciaAlumnoDB.alumno_id == a.id)
                .order_by(AsistenciaAlumnoDB.fecha_clase.desc())
                .first()
        }
        for a in alumnos
    ]


@router.get("/asistencia/top-alumnos", response_model=List[dict])
def top_alumnos_asistencia(
    limite: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Top alumnos con mejor asistencia"""
    
    alumnos = db.query(AlumnoDB).filter(AlumnoDB.activo == True).all()
    
    ranking = []
    for a in alumnos:
        total_asistencias = db.query(AsistenciaAlumnoDB).filter(
            AsistenciaAlumnoDB.alumno_id == a.id,
            AsistenciaAlumnoDB.presente == True
        ).count()
        
        ranking.append({
            "id": a.id,
            "nombre": a.nombre_completo,
            "total_asistencias": total_asistencias,
            "porcentaje_asistencia": round(total_asistencias / a.asistencias_totales * 100, 1) if a.asistencias_totales > 0 else 0
        })
    
    ranking.sort(key=lambda x: x["porcentaje_asistencia"], reverse=True)
    
    return ranking[:limite]


# ==================== REPORTES POR EDAD Y CATEGORÍA ====================

@router.get("/demografia/edades", response_model=dict)
def distribucion_edades(
    db: Session = Depends(get_db)
):
    """Distribución de alumnos por rango de edad"""
    
    alumnos = db.query(AlumnoDB).filter(AlumnoDB.activo == True).all()
    
    rangos = {
        "4-7 años": 0,
        "8-12 años": 0,
        "13-17 años": 0,
        "18-25 años": 0,
        "26-35 años": 0,
        "36-50 años": 0,
        "50+ años": 0
    }
    
    for a in alumnos:
        edad = a.edad
        if edad <= 7:
            rangos["4-7 años"] += 1
        elif edad <= 12:
            rangos["8-12 años"] += 1
        elif edad <= 17:
            rangos["13-17 años"] += 1
        elif edad <= 25:
            rangos["18-25 años"] += 1
        elif edad <= 35:
            rangos["26-35 años"] += 1
        elif edad <= 50:
            rangos["36-50 años"] += 1
        else:
            rangos["50+ años"] += 1
    
    return {
        "total_alumnos": len(alumnos),
        "distribucion": rangos
    }


@router.get("/demografia/categorias", response_model=dict)
def distribucion_categorias(
    db: Session = Depends(get_db)
):
    """Distribución de alumnos por categoría WAKO"""
    
    alumnos = db.query(AlumnoDB).filter(AlumnoDB.activo == True).all()
    
    categorias = {}
    for a in alumnos:
        cat = a.categoria_generica.split(" | ")[0]  # Solo la división
        categorias[cat] = categorias.get(cat, 0) + 1
    
    return {
        "total_alumnos": len(alumnos),
        "por_categoria": categorias
    }


# ==================== REPORTES DE RENDIMIENTO ====================

@router.get("/rendimiento/medallero", response_model=List[dict])
def medallero_general(
    limite: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Alumnos con más medallas"""
    
    from app.models import LogroDB
    
    medallas = db.query(LogroDB).filter(
        LogroDB.medalla.in_(["Oro", "Plata", "Bronce"])
    ).all()
    
    conteo = {}
    for m in medallas:
        if m.alumno_id not in conteo:
            conteo[m.alumno_id] = {"oro": 0, "plata": 0, "bronce": 0, "total": 0}
        
        conteo[m.alumno_id][m.medalla.lower()] += 1
        conteo[m.alumno_id]["total"] += 1
    
    ranking = []
    for alumno_id, stats in conteo.items():
        alumno = db.query(AlumnoDB).get(alumno_id)
        if alumno:
            ranking.append({
                "id": alumno.id,
                "nombre": alumno.nombre_completo,
                "oro": stats["oro"],
                "plata": stats["plata"],
                "bronce": stats["bronce"],
                "total": stats["total"]
            })
    
    ranking.sort(key=lambda x: (x["oro"], x["plata"], x["bronce"]), reverse=True)
    
    return ranking[:limite]


@router.get("/rendimiento/tecnicas", response_model=List[dict])
def tecnicas_mas_dominadas(
    limite: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Técnicas más dominadas por los alumnos"""
    
    from app.models import TecnicaDominadaDB
    from sqlalchemy import func
    
    tecnicas = db.query(
        TecnicaDominadaDB.nombre_tecnica,
        func.count(TecnicaDominadaDB.id).label('total'),
        func.avg(TecnicaDominadaDB.nivel_dominio).label('nivel_promedio')
    ).group_by(TecnicaDominadaDB.nombre_tecnica).all()
    
    resultados = []
    for t in tecnicas:
        resultados.append({
            "tecnica": t.nombre_tecnica,
            "alumnos_que_la_dominan": t.total,
            "nivel_promedio": round(t.nivel_promedio, 1)
        })
    
    resultados.sort(key=lambda x: x["alumnos_que_la_dominan"], reverse=True)
    
    return resultados[:limite]


# ==================== REPORTES DE VENCIMIENTOS ====================

@router.get("/vencimientos/certificados-medicos", response_model=List[dict])
def certificados_por_vencer(
    dias: int = Query(30, ge=1, le=180),
    db: Session = Depends(get_db)
):
    """Alumnos con certificados médicos próximos a vencer"""
    
    fecha_limite = date.today() + timedelta(days=dias)
    
    alumnos = db.query(AlumnoDB).filter(
        AlumnoDB.activo == True,
        AlumnoDB.expediente.has(
            ExpedienteDB.fecha_certificado_medico <= fecha_limite,
            ExpedienteDB.fecha_certificado_medico >= date.today()
        )
    ).all()
    
    return [
        {
            "id": a.id,
            "nombre": a.nombre_completo,
            "fecha_certificado": a.expediente.fecha_certificado_medico,
            "dias_restantes": (a.expediente.fecha_certificado_medico + timedelta(days=365) - date.today()).days,
            "telefono": a.telefono_celular
        }
        for a in alumnos if a.expediente and a.expediente.fecha_certificado_medico
    ]