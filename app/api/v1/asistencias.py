# app/api/v1/asistencias.py
"""Endpoints para gestión de asistencias"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.models import (
    AsistenciaAlumnoDB, HorarioClaseDB, AlumnoDB, 
    InscripcionClaseDB, AsistenciaMaestroDB, MaestroDB
)
from app.schemas import (
    AsistenciaAlumnoCreate, AsistenciaAlumnoResponse,
    TomaAsistenciaMasiva, MessageResponse
)

router = APIRouter()


# ==================== ASISTENCIA DE ALUMNOS ====================

@router.post("/alumnos", response_model=AsistenciaAlumnoResponse)
def registrar_asistencia_alumno(
    asistencia: AsistenciaAlumnoCreate,
    db: Session = Depends(get_db)
):
    """Registrar asistencia individual de un alumno"""
    
    # Verificar alumno
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == asistencia.alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Verificar horario
    horario = db.query(HorarioClaseDB).filter(HorarioClaseDB.id == asistencia.horario_id).first()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    # Verificar no duplicado (mismo alumno, misma clase, misma fecha)
    existing = db.query(AsistenciaAlumnoDB).filter(
        AsistenciaAlumnoDB.alumno_id == asistencia.alumno_id,
        AsistenciaAlumnoDB.horario_id == asistencia.horario_id,
        AsistenciaAlumnoDB.fecha_clase == asistencia.fecha_clase
    ).first()
    
    if existing:
        # Actualizar existente
        existing.presente = asistencia.presente
        existing.hora_llegada = asistencia.hora_llegada
        existing.minutos_tardia = asistencia.minutos_tardia
        existing.observaciones = asistencia.observaciones
        db.commit()
        db.refresh(existing)
        return existing
    
    db_asistencia = AsistenciaAlumnoDB(**asistencia.model_dump())
    db.add(db_asistencia)
    db.commit()
    db.refresh(db_asistencia)
    
    return db_asistencia


@router.post("/tomar-lista", response_model=MessageResponse)
def tomar_lista_asistencia(
    data: TomaAsistenciaMasiva,
    db: Session = Depends(get_db)
):
    """Tomar asistencia masiva para una clase"""
    
    # Verificar horario
    horario = db.query(HorarioClaseDB).filter(HorarioClaseDB.id == data.horario_id).first()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    # Obtener todos los alumnos inscritos activos
    inscritos = db.query(InscripcionClaseDB).filter(
        InscripcionClaseDB.horario_id == data.horario_id,
        InscripcionClaseDB.activo == True
    ).all()
    
    alumnos_ids = [i.alumno_id for i in inscritos]
    
    # Registrar asistencias
    registrados = 0
    actualizados = 0
    
    for alumno_id in data.presentes:
        if alumno_id not in alumnos_ids:
            continue
        
        existing = db.query(AsistenciaAlumnoDB).filter(
            AsistenciaAlumnoDB.alumno_id == alumno_id,
            AsistenciaAlumnoDB.horario_id == data.horario_id,
            AsistenciaAlumnoDB.fecha_clase == data.fecha_clase
        ).first()
        
        if existing:
            existing.presente = True
            actualizados += 1
        else:
            nueva = AsistenciaAlumnoDB(
                alumno_id=alumno_id,
                horario_id=data.horario_id,
                fecha_clase=data.fecha_clase,
                presente=True
            )
            db.add(nueva)
            registrados += 1
    
    # Marcar ausentes explícitamente (opcional)
    for alumno_id in data.ausentes:
        if alumno_id not in alumnos_ids:
            continue
        
        existing = db.query(AsistenciaAlumnoDB).filter(
            AsistenciaAlumnoDB.alumno_id == alumno_id,
            AsistenciaAlumnoDB.horario_id == data.horario_id,
            AsistenciaAlumnoDB.fecha_clase == data.fecha_clase
        ).first()
        
        if not existing:
            nueva = AsistenciaAlumnoDB(
                alumno_id=alumno_id,
                horario_id=data.horario_id,
                fecha_clase=data.fecha_clase,
                presente=False
            )
            db.add(nueva)
            registrados += 1
    
    db.commit()
    
    return MessageResponse(
        message=f"Lista tomada: {registrados} nuevas, {actualizados} actualizadas",
        details=f"Total alumnos en clase: {len(alumnos_ids)}"
    )


@router.get("/clase/{horario_id}", response_model=List[AsistenciaAlumnoResponse])
def obtener_asistencias_clase(
    horario_id: int,
    fecha: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Obtener asistencias de una clase en una fecha específica"""
    
    if not fecha:
        fecha = date.today()
    
    asistencias = db.query(AsistenciaAlumnoDB).filter(
        AsistenciaAlumnoDB.horario_id == horario_id,
        AsistenciaAlumnoDB.fecha_clase == fecha
    ).all()
    
    return asistencias


@router.get("/alumno/{alumno_id}", response_model=List[AsistenciaAlumnoResponse])
def obtener_asistencias_alumno(
    alumno_id: int,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Obtener historial de asistencias de un alumno"""
    
    query = db.query(AsistenciaAlumnoDB).filter(
        AsistenciaAlumnoDB.alumno_id == alumno_id
    )
    
    if desde:
        query = query.filter(AsistenciaAlumnoDB.fecha_clase >= desde)
    if hasta:
        query = query.filter(AsistenciaAlumnoDB.fecha_clase <= hasta)
    
    asistencias = query.order_by(AsistenciaAlumnoDB.fecha_clase.desc()).all()
    return asistencias


# ==================== ASISTENCIA DE MAESTROS ====================

@router.post("/maestros", response_model=dict)
def registrar_asistencia_maestro(
    maestro_id: int,
    horario_id: int,
    fecha_clase: date = date.today(),
    presente: bool = True,
    es_suplente: bool = False,
    sustituto_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Registrar asistencia de un maestro a su clase"""
    
    # Verificar maestro
    maestro = db.query(MaestroDB).filter(MaestroDB.id == maestro_id).first()
    if not maestro:
        raise HTTPException(status_code=404, detail="Maestro no encontrado")
    
    # Verificar horario
    horario = db.query(HorarioClaseDB).filter(HorarioClaseDB.id == horario_id).first()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    # Verificar no duplicado
    existing = db.query(AsistenciaMaestroDB).filter(
        AsistenciaMaestroDB.maestro_id == maestro_id,
        AsistenciaMaestroDB.horario_id == horario_id,
        AsistenciaMaestroDB.fecha_clase == fecha_clase
    ).first()
    
    if existing:
        existing.presente = presente
        existing.es_suplente = es_suplente
        existing.sustituto_id = sustituto_id
        db.commit()
        return {"message": "Asistencia actualizada", "maestro": maestro.nombre_completo}
    
    nueva = AsistenciaMaestroDB(
        maestro_id=maestro_id,
        horario_id=horario_id,
        fecha_clase=fecha_clase,
        presente=presente,
        es_suplente=es_suplente,
        sustituto_id=sustituto_id
    )
    
    db.add(nueva)
    db.commit()
    
    return {"message": "Asistencia registrada", "maestro": maestro.nombre_completo}


# ==================== REPORTES DE ASISTENCIA ====================

@router.get("/reporte/mensual", response_model=dict)
def reporte_asistencia_mensual(
    anio: int,
    mes: int,
    db: Session = Depends(get_db)
):
    """Reporte de asistencia mensual por alumno"""
    
    # Calcular días del mes
    from calendar import monthrange
    _, ultimo_dia = monthrange(anio, mes)
    
    fecha_inicio = date(anio, mes, 1)
    fecha_fin = date(anio, mes, ultimo_dia)
    
    # Obtener asistencias del mes
    asistencias = db.query(AsistenciaAlumnoDB).filter(
        AsistenciaAlumnoDB.fecha_clase >= fecha_inicio,
        AsistenciaAlumnoDB.fecha_clase <= fecha_fin,
        AsistenciaAlumnoDB.presente == True
    ).all()
    
    # Agrupar por alumno
    resumen = {}
    for a in asistencias:
        if a.alumno_id not in resumen:
            resumen[a.alumno_id] = {
                "nombre": a.alumno.nombre_completo,
                "asistencias": 0
            }
        resumen[a.alumno_id]["asistencias"] += 1
    
    return {
        "anio": anio,
        "mes": mes,
        "total_asistencias": len(asistencias),
        "alumnos_con_asistencia": len(resumen),
        "detalle": list(resumen.values())
    }


@router.get("/reporte/clase/{horario_id}", response_model=dict)
def reporte_asistencia_clase(
    horario_id: int,
    desde: date,
    hasta: date,
    db: Session = Depends(get_db)
):
    """Reporte de asistencia para una clase específica en un período"""
    
    asistencias = db.query(AsistenciaAlumnoDB).filter(
        AsistenciaAlumnoDB.horario_id == horario_id,
        AsistenciaAlumnoDB.fecha_clase >= desde,
        AsistenciaAlumnoDB.fecha_clase <= hasta
    ).all()
    
    total_clases = len(set(a.fecha_clase for a in asistencias))
    alumnos_unicos = len(set(a.alumno_id for a in asistencias))
    
    return {
        "horario_id": horario_id,
        "periodo": {"desde": desde, "hasta": hasta},
        "total_clases": total_clases,
        "total_asistencias_registradas": len(asistencias),
        "alumnos_diferentes": alumnos_unicos,
        "promedio_por_clase": round(len(asistencias) / total_clases, 2) if total_clases > 0 else 0
    }