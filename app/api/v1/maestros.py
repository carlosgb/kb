# app/api/v1/maestros.py
"""Endpoints para gestión de maestros"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from app.core.database import get_db
from app.models import MaestroDB, HorarioClaseDB
from app.schemas import (
    MaestroCreate, MaestroUpdate, MaestroResponse,
    HorarioClaseResponse, MessageResponse
)

router = APIRouter()


# ==================== CRUD BÁSICO ====================

@router.post("/", response_model=MaestroResponse, status_code=status.HTTP_201_CREATED)
def crear_maestro(
    maestro: MaestroCreate,
    db: Session = Depends(get_db)
):
    """Registrar un nuevo maestro/instructor"""
    
    # Validar email único
    existing = db.query(MaestroDB).filter(MaestroDB.email == maestro.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    db_maestro = MaestroDB(**maestro.model_dump())
    db.add(db_maestro)
    db.commit()
    db.refresh(db_maestro)
    
    return db_maestro


@router.get("/", response_model=List[MaestroResponse])
def listar_maestros(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    activo: Optional[bool] = None,
    especialidad: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar maestros con filtros"""
    
    query = db.query(MaestroDB)
    
    if activo is not None:
        query = query.filter(MaestroDB.activo == activo)
    if especialidad:
        query = query.filter(MaestroDB.especialidad == especialidad)
    if search:
        query = query.filter(
            (MaestroDB.nombre.contains(search)) |
            (MaestroDB.apellidos.contains(search)) |
            (MaestroDB.email.contains(search))
        )
    
    maestros = query.offset(skip).limit(limit).all()
    return maestros


@router.get("/{maestro_id}", response_model=MaestroResponse)
def obtener_maestro(
    maestro_id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalles de un maestro"""
    
    maestro = db.query(MaestroDB).filter(MaestroDB.id == maestro_id).first()
    if not maestro:
        raise HTTPException(status_code=404, detail="Maestro no encontrado")
    
    return maestro


@router.put("/{maestro_id}", response_model=MaestroResponse)
def actualizar_maestro(
    maestro_id: int,
    maestro_update: MaestroUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar datos de un maestro"""
    
    maestro = db.query(MaestroDB).filter(MaestroDB.id == maestro_id).first()
    if not maestro:
        raise HTTPException(status_code=404, detail="Maestro no encontrado")
    
    update_data = maestro_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(maestro, field, value)
    
    db.commit()
    db.refresh(maestro)
    
    return maestro


@router.delete("/{maestro_id}", response_model=MessageResponse)
def eliminar_maestro(
    maestro_id: int,
    hard_delete: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Eliminar o desactivar maestro"""
    
    maestro = db.query(MaestroDB).filter(MaestroDB.id == maestro_id).first()
    if not maestro:
        raise HTTPException(status_code=404, detail="Maestro no encontrado")
    
    if hard_delete:
        db.delete(maestro)
        message = "Maestro eliminado permanentemente"
    else:
        maestro.activo = False
        message = "Maestro desactivado"
    
    db.commit()
    
    return MessageResponse(message=message)


# ==================== HORARIOS DEL MAESTRO ====================

@router.get("/{maestro_id}/horarios", response_model=List[HorarioClaseResponse])
def obtener_horarios_maestro(
    maestro_id: int,
    activo: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Obtener todos los horarios de un maestro"""
    
    maestro = db.query(MaestroDB).filter(MaestroDB.id == maestro_id).first()
    if not maestro:
        raise HTTPException(status_code=404, detail="Maestro no encontrado")
    
    query = db.query(HorarioClaseDB).filter(HorarioClaseDB.maestro_id == maestro_id)
    
    if activo is not None:
        query = query.filter(HorarioClaseDB.activo == activo)
    
    horarios = query.order_by(HorarioClaseDB.dia_semana, HorarioClaseDB.hora_inicio).all()
    return horarios


@router.get("/{maestro_id}/horarios/hoy", response_model=List[HorarioClaseResponse])
def obtener_horarios_hoy(
    maestro_id: int,
    db: Session = Depends(get_db)
):
    """Obtener horarios del maestro para hoy"""
    
    from datetime import datetime
    
    dia_hoy = datetime.now().weekday()  # 0=Lunes
    
    horarios = db.query(HorarioClaseDB).filter(
        HorarioClaseDB.maestro_id == maestro_id,
        HorarioClaseDB.dia_semana == dia_hoy,
        HorarioClaseDB.activo == True
    ).order_by(HorarioClaseDB.hora_inicio).all()
    
    return horarios


# ==================== ESTADÍSTICAS ====================

@router.get("/{maestro_id}/estadisticas", response_model=dict)
def obtener_estadisticas_maestro(
    maestro_id: int,
    db: Session = Depends(get_db)
):
    """Obtener estadísticas del maestro"""
    
    maestro = db.query(MaestroDB).filter(MaestroDB.id == maestro_id).first()
    if not maestro:
        raise HTTPException(status_code=404, detail="Maestro no encontrado")
    
    # Calcular asistencias del mes
    from datetime import date, timedelta
    primer_dia_mes = date.today().replace(day=1)
    
    asistencias_mes = db.query(models.AsistenciaMaestroDB).filter(
        models.AsistenciaMaestroDB.maestro_id == maestro_id,
        models.AsistenciaMaestroDB.fecha_clase >= primer_dia_mes,
        models.AsistenciaMaestroDB.presente == True
    ).count()
    
    return {
        "maestro": maestro.nombre_completo,
        "horas_semana": maestro.horas_semana,
        "alumnos_totales": maestro.alumnos_totales,
        "clases_activas": len([h for h in maestro.horarios if h.activo]),
        "asistencias_mes": asistencias_mes,
        "sueldo_mensual_estimado": maestro.sueldo_base + (maestro.comision_por_clase * len(maestro.horarios) * 4)
    }