# app/api/v1/eventos.py
"""Endpoints para gestión de eventos y torneos"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from app.core.database import get_db
from app.models import EventoDB, InscripcionEventoDB, AlumnoDB
from app.schemas import (
    EventoCreate, EventoUpdate, EventoResponse,
    InscripcionEventoCreate, InscripcionEventoResponse,
    MessageResponse
)

router = APIRouter()


# ==================== CRUD EVENTOS ====================

@router.post("/", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
def crear_evento(
    evento: EventoCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo evento/torneo"""
    
    db_evento = EventoDB(**evento.model_dump())
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    
    return db_evento


@router.get("/", response_model=List[EventoResponse])
def listar_eventos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo: Optional[str] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    activo: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Listar eventos con filtros"""
    
    query = db.query(EventoDB)
    
    if tipo:
        query = query.filter(EventoDB.tipo == tipo)
    if desde:
        query = query.filter(EventoDB.fecha >= desde)
    if hasta:
        query = query.filter(EventoDB.fecha <= hasta)
    if activo is not None:
        query = query.filter(EventoDB.activo == activo)
    
    eventos = query.order_by(EventoDB.fecha).offset(skip).limit(limit).all()
    return eventos


@router.get("/proximos", response_model=List[EventoResponse])
def eventos_proximos(
    dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Listar eventos próximos en los próximos X días"""
    
    hoy = date.today()
    fecha_limite = date.today().replace(day=hoy.day + dias) if dias <= 28 else hoy + __import__('datetime').timedelta(days=dias)
    
    from datetime import timedelta
    fecha_limite = hoy + timedelta(days=dias)
    
    eventos = db.query(EventoDB).filter(
        EventoDB.fecha >= hoy,
        EventoDB.fecha <= fecha_limite,
        EventoDB.activo == True
    ).order_by(EventoDB.fecha).all()
    
    return eventos


@router.get("/{evento_id}", response_model=EventoResponse)
def obtener_evento(
    evento_id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalles de un evento"""
    
    evento = db.query(EventoDB).filter(EventoDB.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    return evento


@router.put("/{evento_id}", response_model=EventoResponse)
def actualizar_evento(
    evento_id: int,
    evento_update: EventoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar datos de un evento"""
    
    evento = db.query(EventoDB).filter(EventoDB.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    update_data = evento_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evento, field, value)
    
    db.commit()
    db.refresh(evento)
    
    return evento

@router.delete("/{evento_id}", response_model=MessageResponse)
def eliminar_evento(
    evento_id: int,
    hard_delete: bool = Query(False, description="Eliminar físicamente"),
    db: Session = Depends(get_db)
):
    """Eliminar o desactivar un evento"""
    
    evento = db.query(EventoDB).filter(EventoDB.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    if hard_delete:
        db.delete(evento)
        message = "Evento eliminado permanentemente"
    else:
        evento.activo = False
        message = "Evento desactivado"
    
    db.commit()
    
    return MessageResponse(message=message)


# ==================== INSCRIPCIONES ====================

# app/api/v1/eventos.py - Corregir la función inscribir_alumno

@router.post("/{evento_id}/inscribir", response_model=InscripcionEventoResponse)
def inscribir_alumno(
    evento_id: int,
    inscripcion: InscripcionEventoCreate,
    alumno_id: int = Query(..., description="ID del alumno a inscribir"),
    db: Session = Depends(get_db)
):
    """Inscribir un alumno a un evento"""
    
    # Verificar evento
    evento = db.query(EventoDB).filter(EventoDB.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # Verificar inscripción abierta
    if not evento.inscripcion_abierta:
        raise HTTPException(status_code=400, detail="Inscripciones cerradas para este evento")
    
    # Verificar alumno
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Verificar no duplicado
    existing = db.query(InscripcionEventoDB).filter(
        InscripcionEventoDB.evento_id == evento_id,
        InscripcionEventoDB.alumno_id == alumno_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Alumno ya inscrito en este evento")
    
    # Crear inscripción
    db_inscripcion = InscripcionEventoDB(
        evento_id=evento_id,
        alumno_id=alumno_id,
        num_acompañantes=inscripcion.num_acompañantes,
        categoria_inscrita=inscripcion.categoria_inscrita,
        peso_registrado=inscripcion.peso_registrado,
        fecha_inscripcion=date.today(),
        pagado=False,
        cancelada=False
    )
    
    db.add(db_inscripcion)
    db.commit()
    db.refresh(db_inscripcion)
    
    # Construir respuesta manualmente para evitar errores
    return {
        "id": db_inscripcion.id,
        "alumno_id": db_inscripcion.alumno_id,
        "alumno_nombre": f"{alumno.nombre} {alumno.apellidos}",
        "evento_id": db_inscripcion.evento_id,
        "evento_titulo": evento.titulo,
        "num_acompañantes": db_inscripcion.num_acompañantes,
        "pagado": db_inscripcion.pagado,
        "total_a_pagar": db_inscripcion.total_a_pagar,
        "fecha_inscripcion": db_inscripcion.fecha_inscripcion,
        "cancelada": db_inscripcion.cancelada
    }


# app/api/v1/eventos.py - Corregir listar_inscritos

@router.get("/{evento_id}/inscritos", response_model=List[InscripcionEventoResponse])
def listar_inscritos(
    evento_id: int,
    solo_pagados: bool = False,
    db: Session = Depends(get_db)
):
    """Listar alumnos inscritos en un evento"""
    
    query = db.query(InscripcionEventoDB).filter(
        InscripcionEventoDB.evento_id == evento_id,
        InscripcionEventoDB.cancelada == False
    )
    
    if solo_pagados:
        query = query.filter(InscripcionEventoDB.pagado == True)
    
    inscritos = query.all()
    
    # Construir respuesta manualmente
    resultados = []
    for ins in inscritos:
        alumno = db.query(AlumnoDB).filter(AlumnoDB.id == ins.alumno_id).first()
        evento = db.query(EventoDB).filter(EventoDB.id == ins.evento_id).first()
        
        resultados.append({
            "id": ins.id,
            "alumno_id": ins.alumno_id,
            "alumno_nombre": f"{alumno.nombre} {alumno.apellidos}" if alumno else None,
            "evento_id": ins.evento_id,
            "evento_titulo": evento.titulo if evento else None,
            "num_acompañantes": ins.num_acompañantes,
            "pagado": ins.pagado,
            "total_a_pagar": ins.total_a_pagar,
            "fecha_inscripcion": ins.fecha_inscripcion,
            "cancelada": ins.cancelada
        })
    
    return resultados


@router.put("/inscripciones/{inscripcion_id}/pagar", response_model=InscripcionEventoResponse)
def confirmar_pago_inscripcion(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    """Confirmar pago de inscripción a evento"""
    
    inscripcion = db.query(InscripcionEventoDB).filter(
        InscripcionEventoDB.id == inscripcion_id
    ).first()
    
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    
    inscripcion.pagado = True
    db.commit()
    db.refresh(inscripcion)
    
    return inscripcion


@router.delete("/inscripciones/{inscripcion_id}", response_model=MessageResponse)
def cancelar_inscripcion(
    inscripcion_id: int,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Cancelar inscripción de un alumno a un evento"""
    
    inscripcion = db.query(InscripcionEventoDB).filter(
        InscripcionEventoDB.id == inscripcion_id
    ).first()
    
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    
    inscripcion.cancelada = True
    inscripcion.motivo_cancelacion = motivo
    
    db.commit()
    
    return MessageResponse(message="Inscripción cancelada", details=motivo)


# ==================== REPORTES DEL EVENTO ====================

@router.get("/{evento_id}/resumen", response_model=dict)
def resumen_evento(
    evento_id: int,
    db: Session = Depends(get_db)
):
    """Obtener resumen operativo y financiero del evento"""
    
    evento = db.query(EventoDB).filter(EventoDB.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    inscritos = [i for i in evento.participantes if not i.cancelada]
    pagados = [i for i in inscritos if i.pagado]
    
    total_acompañantes = sum(i.num_acompañantes for i in inscritos)
    ingresos_totales = sum(i.total_a_pagar for i in inscritos)
    ingresos_confirmados = sum(i.total_a_pagar for i in pagados)
    
    return {
        "evento": {
            "id": evento.id,
            "titulo": evento.titulo,
            "fecha": evento.fecha,
            "lugar": evento.lugar
        },
        "inscripciones": {
            "total": len(inscritos),
            "pagados": len(pagados),
            "pendientes": len(inscritos) - len(pagados),
            "canceladas": len([i for i in evento.participantes if i.cancelada])
        },
        "acompañantes": {
            "total": total_acompañantes,
            "promedio_por_alumno": round(total_acompañantes / len(inscritos), 2) if inscritos else 0
        },
        "finanzas": {
            "ingresos_totales": ingresos_totales,
            "ingresos_confirmados": ingresos_confirmados,
            "ingresos_pendientes": ingresos_totales - ingresos_confirmados
        }
    }