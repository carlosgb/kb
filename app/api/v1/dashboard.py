# app/api/v1/dashboard.py
"""Endpoints para dashboard y KPIs"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from calendar import monthrange

from app.core.database import get_db
from app.models import (
    AlumnoDB, MaestroDB, EventoDB, HorarioClaseDB,
    AsistenciaAlumnoDB, ContratoSeguroDB
)

router = APIRouter()


@router.get("/resumen", response_model=dict)
def dashboard_resumen(
    db: Session = Depends(get_db)
):
    """Resumen general del dashboard"""
    
    hoy = date.today()
    primer_dia_mes = hoy.replace(day=1)
    
    # Conteos básicos
    total_alumnos = db.query(AlumnoDB).filter(AlumnoDB.activo == True).count()
    total_maestros = db.query(MaestroDB).filter(MaestroDB.activo == True).count()
    total_eventos = db.query(EventoDB).filter(EventoDB.fecha >= hoy, EventoDB.activo == True).count()
    clases_hoy = db.query(HorarioClaseDB).filter(
        HorarioClaseDB.dia_semana == datetime.now().weekday(),
        HorarioClaseDB.activo == True
    ).count()
    
    # Alumnos nuevos este mes
    nuevos_alumnos = db.query(AlumnoDB).filter(
        AlumnoDB.fecha_registro >= primer_dia_mes
    ).count()
    
    # Asistencias del mes
    asistencias_mes = db.query(AsistenciaAlumnoDB).filter(
        AsistenciaAlumnoDB.fecha_clase >= primer_dia_mes,
        AsistenciaAlumnoDB.presente == True
    ).count()
    
    # Pagos del mes (alumnos que pagaron este mes)
    pagos_mes = db.query(AlumnoDB).filter(
        AlumnoDB.fecha_ultimo_pago >= primer_dia_mes
    ).count()
    
    # Ingreso estimado del mes
    ingreso_estimado = pagos_mes * 500  # Mensualidad promedio
    
    # Seguros vigentes
    seguros_vigentes = db.query(ContratoSeguroDB).filter(
        ContratoSeguroDB.activo == True,
        ContratoSeguroDB.fecha_fin >= hoy
    ).count()
    
    # Porcentajes
    porcentaje_pago = round((pagos_mes / total_alumnos) * 100, 1) if total_alumnos > 0 else 0
    
    return {
        "resumen": {
            "alumnos_activos": total_alumnos,
            "maestros_activos": total_maestros,
            "eventos_proximos": total_eventos,
            "clases_hoy": clases_hoy
        },
        "mes_actual": {
            "nuevos_alumnos": nuevos_alumnos,
            "asistencias": asistencias_mes,
            "pagos_registrados": pagos_mes,
            "ingreso_estimado": ingreso_estimado,
            "porcentaje_cobertura_pagos": porcentaje_pago,
            "seguros_vigentes": seguros_vigentes
        }
    }


@router.get("/alertas", response_model=dict)
def dashboard_alertas(
    db: Session = Depends(get_db)
):
    """Alertas y notificaciones importantes"""
    
    hoy = date.today()
    
    # Alertas de pagos vencidos (más de 30 días)
    fecha_limite_pago = hoy - timedelta(days=30)
    pagos_vencidos = db.query(AlumnoDB).filter(
        AlumnoDB.activo == True,
        AlumnoDB.fecha_ultimo_pago <= fecha_limite_pago
    ).count()
    
    # Alertas de certificados médicos por vencer (próximos 30 días)
    fecha_limite_cert = hoy + timedelta(days=30)
    certificados_por_vencer = 0
    alumnos_con_certificado = db.query(AlumnoDB).filter(AlumnoDB.activo == True).all()
    for a in alumnos_con_certificado:
        if a.expediente and a.expediente.fecha_certificado_medico:
            vencimiento = a.expediente.fecha_certificado_medico + timedelta(days=365)
            if hoy <= vencimiento <= fecha_limite_cert:
                certificados_por_vencer += 1
    
    # Alertas de seguros por vencer
    seguros_por_vencer = db.query(ContratoSeguroDB).filter(
        ContratoSeguroDB.activo == True,
        ContratoSeguroDB.fecha_fin <= fecha_limite_cert,
        ContratoSeguroDB.fecha_fin >= hoy
    ).count()
    
    # Clases sin maestro asignado
    clases_sin_maestro = db.query(HorarioClaseDB).filter(
        HorarioClaseDB.activo == True,
        HorarioClaseDB.maestro_id.is_(None)
    ).count()
    
    # Eventos con inscripciones próximas a cerrar
    eventos_cierre = db.query(EventoDB).filter(
        EventoDB.activo == True,
        EventoDB.fecha_cierre_inscripcion.isnot(None),
        EventoDB.fecha_cierre_inscripcion <= fecha_limite_cert,
        EventoDB.fecha_cierre_inscripcion >= hoy
    ).count()
    
    # Calcular nivel de riesgo (0-3)
    riesgo = 0
    if pagos_vencidos > 10:
        riesgo += 1
    if certificados_por_vencer > 5:
        riesgo += 1
    if clases_sin_maestro > 2:
        riesgo += 1
    
    return {
        "criticas": {
            "pagos_vencidos": pagos_vencidos,
            "certificados_por_vencer": certificados_por_vencer,
            "seguros_por_vencer": seguros_por_vencer
        },
        "advertencias": {
            "clases_sin_maestro": clases_sin_maestro,
            "eventos_cierre_proximo": eventos_cierre
        },
        "nivel_riesgo": riesgo,
        "recomendaciones": _generar_recomendaciones(pagos_vencidos, certificados_por_vencer, clases_sin_maestro)
    }


def _generar_recomendaciones(pagos_vencidos, certificados_vencer, clases_sin_maestro):
    """Generar recomendaciones basadas en alertas"""
    recomendaciones = []
    
    if pagos_vencidos > 0:
        recomendaciones.append(f"⚠️ {pagos_vencidos} alumnos tienen pagos vencidos. Considerar recordatorio masivo.")
    
    if certificados_vencer > 0:
        recomendaciones.append(f"📋 {certificados_vencer} alumnos necesitan renovar su certificado médico en los próximos 30 días.")
    
    if clases_sin_maestro > 0:
        recomendaciones.append(f"👨‍🏫 {clases_sin_maestro} clases no tienen profesor asignado. Asignar urgentemente.")
    
    if not recomendaciones:
        recomendaciones.append("✅ Todo en orden. Buen trabajo!")
    
    return recomendaciones


@router.get("/tendencias", response_model=dict)
def dashboard_tendencias(
    meses: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Tendencias de los últimos meses"""
    
    tendencias = []
    
    for i in range(meses - 1, -1, -1):
        fecha = date.today().replace(day=1)
        # Restar meses
        mes = fecha.month - i
        anio = fecha.year
        if mes <= 0:
            mes += 12
            anio -= 1
        
        primer_dia = date(anio, mes, 1)
        _, ultimo_dia = monthrange(anio, mes)
        ultimo_dia = date(anio, mes, ultimo_dia)
        
        # Alumnos nuevos en el mes
        nuevos = db.query(AlumnoDB).filter(
            AlumnoDB.fecha_registro >= primer_dia,
            AlumnoDB.fecha_registro <= ultimo_dia
        ).count()
        
        # Asistencias en el mes
        asistencias = db.query(AsistenciaAlumnoDB).filter(
            AsistenciaAlumnoDB.fecha_clase >= primer_dia,
            AsistenciaAlumnoDB.fecha_clase <= ultimo_dia,
            AsistenciaAlumnoDB.presente == True
        ).count()
        
        # Pagos en el mes
        pagos = db.query(AlumnoDB).filter(
            AlumnoDB.fecha_ultimo_pago >= primer_dia,
            AlumnoDB.fecha_ultimo_pago <= ultimo_dia
        ).count()
        
        tendencias.append({
            "mes": f"{anio}-{mes:02d}",
            "nuevos_alumnos": nuevos,
            "asistencias": asistencias,
            "pagos": pagos
        })
    
    return {
        "tendencias": tendencias,
        "resumen": {
            "total_nuevos": sum(t["nuevos_alumnos"] for t in tendencias),
            "promedio_asistencias": round(sum(t["asistencias"] for t in tendencias) / len(tendencias), 1) if tendencias else 0,
            "promedio_pagos": round(sum(t["pagos"] for t in tendencias) / len(tendencias), 1) if tendencias else 0
        }
    }


@router.get("/ocupacion", response_model=dict)
def dashboard_ocupacion(
    db: Session = Depends(get_db)
):
    """Ocupación de clases por día de semana"""
    
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    ocupacion = []
    for i, dia in enumerate(dias):
        horarios = db.query(HorarioClaseDB).filter(
            HorarioClaseDB.dia_semana == i,
            HorarioClaseDB.activo == True
        ).all()
        
        if horarios:
            total_cupo = sum(h.capacidad_maxima for h in horarios)
            total_inscritos = sum(h.alumnos_inscritos for h in horarios)
            porcentaje = round((total_inscritos / total_cupo) * 100, 1) if total_cupo > 0 else 0
        else:
            total_cupo = 0
            total_inscritos = 0
            porcentaje = 0
        
        ocupacion.append({
            "dia": dia,
            "clases": len(horarios),
            "cupo_total": total_cupo,
            "alumnos_inscritos": total_inscritos,
            "porcentaje_ocupacion": porcentaje
        })
    
    # Clases más llenas
    clases_llenas = db.query(HorarioClaseDB).filter(
        HorarioClaseDB.activo == True
    ).all()
    
    top_clases = sorted(clases_llenas, key=lambda h: h.porcentaje_ocupacion, reverse=True)[:5]
    
    return {
        "por_dia": ocupacion,
        "clases_mas_llenas": [
            {
                "nombre": c.nombre,
                "dia": dias[c.dia_semana],
                "horario": f"{c.hora_inicio} - {c.hora_fin}",
                "ocupacion": f"{c.alumnos_inscritos}/{c.capacidad_maxima} ({c.porcentaje_ocupacion}%)"
            }
            for c in top_clases
        ]
    }