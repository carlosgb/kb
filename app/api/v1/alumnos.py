# app/api/v1/alumnos.py
"""Endpoints para gestión de alumnos"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from app.core.database import get_db
from app.models import AlumnoDB, ExpedienteDB, HistorialPesoDB, HistorialGradoDB, InscripcionClaseDB
from app.schemas import (
    AlumnoCreate, AlumnoUpdate, AlumnoResponse, AlumnoDetailResponse,
    ExpedienteUpdate, ExpedienteResponse,
    HistorialPesoCreate, HistorialPesoResponse,
    HistorialGradoCreate, HistorialGradoResponse,
    TecnicaDominadaCreate, TecnicaDominadaResponse,
    LogroCreate, LogroResponse,
    InscripcionClaseResponse,
    MessageResponse, PaginationParams, PaginatedResponse
)

router = APIRouter()


# ==================== CRUD BÁSICO ====================

@router.post("/", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
def crear_alumno(
    alumno: AlumnoCreate,
    db: Session = Depends(get_db)
):
    """Registrar un nuevo alumno"""
    
    # Validar email único
    if alumno.email:
        existing = db.query(AlumnoDB).filter(AlumnoDB.email == alumno.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Crear alumno
    db_alumno = AlumnoDB(**alumno.model_dump())
    db.add(db_alumno)
    db.flush()  # Para obtener el ID
    
    # Crear expediente vacío
    expediente = ExpedienteDB(
        alumno_id=db_alumno.id,
        contacto_emergencia_nombre="PENDIENTE",
        contacto_emergencia_telefono="0000000000"
    )
    db.add(expediente)
    
    # Registrar peso inicial
    peso_inicial = HistorialPesoDB(
        alumno_id=db_alumno.id,
        peso=alumno.peso_actual
    )
    db.add(peso_inicial)
    
    # Registrar grado inicial
    grado_inicial = HistorialGradoDB(
        alumno_id=db_alumno.id,
        grado=alumno.grado_actual
    )
    db.add(grado_inicial)
    
    db.commit()
    db.refresh(db_alumno)
    
    return db_alumno


@router.get("/", response_model=List[AlumnoResponse])
def listar_alumnos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    activo: Optional[bool] = None,
    es_competidor: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar alumnos con filtros"""
    
    query = db.query(AlumnoDB)
    
    if activo is not None:
        query = query.filter(AlumnoDB.activo == activo)
    if es_competidor is not None:
        query = query.filter(AlumnoDB.es_competidor == es_competidor)
    if search:
        query = query.filter(
            (AlumnoDB.nombre.contains(search)) |
            (AlumnoDB.apellidos.contains(search)) |
            (AlumnoDB.email.contains(search))
        )
    
    alumnos = query.offset(skip).limit(limit).all()
    return alumnos


@router.get("/{alumno_id}", response_model=AlumnoDetailResponse)
def obtener_alumno(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalles completos de un alumno"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Construir respuesta detallada
    response = AlumnoDetailResponse.model_validate(alumno)
    
    # Agregar datos extra
    response.tiene_expediente = alumno.expediente is not None
    if alumno.expediente:
        response.expediente_completado = alumno.expediente.porcentaje_completado
    
    if alumno.membresia_activa:
        response.membresia_activa = {
            "federacion": alumno.membresia_activa.federacion.nombre,
            "numero": alumno.membresia_activa.numero_afiliacion,
            "vigente": alumno.membresia_activa.vigente,
            "dias_restantes": alumno.membresia_activa.dias_restantes
        }
    
    if alumno.seguro_activo:
        response.seguro_activo = alumno.resumen_seguro
    
    response.total_logros = len(alumno.logros)
    response.total_tecnicas = len(alumno.tecnicas)
    
    return response


@router.put("/{alumno_id}", response_model=AlumnoResponse)
def actualizar_alumno(
    alumno_id: int,
    alumno_update: AlumnoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar datos de un alumno"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Actualizar campos
    update_data = alumno_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alumno, field, value)
    
    # Si cambió el peso, registrar en historial
    if 'peso_actual' in update_data:
        nuevo_peso = update_data['peso_actual']
        historial = HistorialPesoDB(
            alumno_id=alumno_id,
            peso=nuevo_peso
        )
        db.add(historial)
    
    db.commit()
    db.refresh(alumno)
    
    return alumno


@router.delete("/{alumno_id}", response_model=MessageResponse)
def eliminar_alumno(
    alumno_id: int,
    hard_delete: bool = Query(False, description="Eliminar físicamente (soft delete por defecto)"),
    db: Session = Depends(get_db)
):
    """Eliminar o desactivar alumno"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    if hard_delete:
        db.delete(alumno)
        message = "Alumno eliminado permanentemente"
    else:
        alumno.activo = False
        message = "Alumno desactivado"
    
    db.commit()
    
    return MessageResponse(message=message)


# ==================== EXPEDIENTE ====================

@router.get("/{alumno_id}/expediente", response_model=ExpedienteResponse)
def obtener_expediente(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    """Obtener expediente del alumno"""
    
    expediente = db.query(ExpedienteDB).filter(ExpedienteDB.alumno_id == alumno_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    
    return expediente


@router.put("/{alumno_id}/expediente", response_model=ExpedienteResponse)
def actualizar_expediente(
    alumno_id: int,
    expediente_data: ExpedienteUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar expediente del alumno"""
    
    expediente = db.query(ExpedienteDB).filter(ExpedienteDB.alumno_id == alumno_id).first()
    
    if not expediente:
        # Crear si no existe
        expediente = ExpedienteDB(alumno_id=alumno_id, **expediente_data.model_dump())
        db.add(expediente)
    else:
        # Actualizar existente
        update_data = expediente_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expediente, field, value)
    
    db.commit()
    db.refresh(expediente)
    
    return expediente


# ==================== TRACKING ====================

@router.post("/{alumno_id}/peso", response_model=HistorialPesoResponse)
def registrar_peso(
    alumno_id: int,
    peso_data: HistorialPesoCreate,
    db: Session = Depends(get_db)
):
    """Registrar nuevo peso en historial y actualizar peso actual"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Registrar en historial
    historial = HistorialPesoDB(
        alumno_id=alumno_id,
        **peso_data.model_dump()
    )
    db.add(historial)
    
    # Actualizar peso actual
    alumno.peso_actual = peso_data.peso
    
    db.commit()
    db.refresh(historial)
    
    return historial


@router.post("/{alumno_id}/ascender", response_model=HistorialGradoResponse)
def registrar_ascenso(
    alumno_id: int,
    grado_data: HistorialGradoCreate,
    db: Session = Depends(get_db)
):
    """Registrar ascenso de grado"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Registrar en historial
    historial = HistorialGradoDB(
        alumno_id=alumno_id,
        **grado_data.model_dump()
    )
    db.add(historial)
    
    # Actualizar grado actual
    alumno.grado_actual = grado_data.grado
    
    db.commit()
    db.refresh(historial)
    
    return historial


@router.post("/{alumno_id}/tecnicas", response_model=TecnicaDominadaResponse)
def agregar_tecnica(
    alumno_id: int,
    tecnica_data: TecnicaDominadaCreate,
    db: Session = Depends(get_db)
):
    """Agregar o actualizar técnica dominada"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    from app.models import TecnicaDominadaDB
    
    # Buscar si ya existe
    existente = db.query(TecnicaDominadaDB).filter(
        TecnicaDominadaDB.alumno_id == alumno_id,
        TecnicaDominadaDB.nombre_tecnica == tecnica_data.nombre_tecnica
    ).first()
    
    if existente:
        existente.nivel_dominio = tecnica_data.nivel_dominio
        existente.observaciones = tecnica_data.observaciones
        db.commit()
        db.refresh(existente)
        return existente
    
    # Crear nueva
    nueva = TecnicaDominadaDB(
        alumno_id=alumno_id,
        **tecnica_data.model_dump()
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    
    return nueva


@router.post("/{alumno_id}/logros", response_model=LogroResponse)
def registrar_logro(
    alumno_id: int,
    logro_data: LogroCreate,
    db: Session = Depends(get_db)
):
    """Registrar logro/medalla del alumno"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    from app.models import LogroDB
    
    logro = LogroDB(
        alumno_id=alumno_id,
        **logro_data.model_dump()
    )
    db.add(logro)
    db.commit()
    db.refresh(logro)
    
    return logro


@router.get("/{alumno_id}/logros", response_model=List[LogroResponse])
def obtener_logros(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    """Obtener todos los logros del alumno"""
    
    from app.models import LogroDB
    
    logros = db.query(LogroDB).filter(LogroDB.alumno_id == alumno_id).all()
    return logros


@router.get("/{alumno_id}/historial-pesos", response_model=List[HistorialPesoResponse])
def obtener_historial_pesos(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    """Obtener historial completo de pesos"""
    
    pesos = db.query(HistorialPesoDB).filter(
        HistorialPesoDB.alumno_id == alumno_id
    ).order_by(HistorialPesoDB.fecha.desc()).all()
    
    return pesos


@router.get("/{alumno_id}/historial-grados", response_model=List[HistorialGradoResponse])
def obtener_historial_grados(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    """Obtener historial de grados/ascensos"""
    
    grados = db.query(HistorialGradoDB).filter(
        HistorialGradoDB.alumno_id == alumno_id
    ).order_by(HistorialGradoDB.fecha_ascenso.desc()).all()
    
    return grados


# ==================== OPERACIONES DIARIAS ====================

@router.put("/{alumno_id}/asistencia", response_model=MessageResponse)
def marcar_asistencia(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    """Marcar asistencia general del alumno"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    alumno.asistencias_totales += 1
    db.commit()
    
    return MessageResponse(
        message="Asistencia registrada",
        details=f"Total asistencias: {alumno.asistencias_totales}"
    )


@router.put("/{alumno_id}/pagar-mensualidad", response_model=MessageResponse)
def pagar_mensualidad(
    alumno_id: int,
    monto_pagado: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Registrar pago de mensualidad"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    alumno.fecha_ultimo_pago = date.today()
    
    # Registrar pago en tabla de pagos si se implementó
    # from app.models import PagoDB
    # pago = PagoDB(...)
    
    db.commit()
    
    return MessageResponse(
        message="Pago registrado",
        details=f"Monto: ${monto_pagado or alumno.monto_con_recargo}"
    )


@router.get("/{alumno_id}/estado-cuenta", response_model=dict)
def estado_cuenta(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    """Obtener estado financiero del alumno"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    return {
        "alumno": alumno.nombre_completo,
        "mensualidad_actual": alumno.monto_mensualidad,
        "monto_con_recargo": alumno.monto_con_recargo,
        "ultimo_pago": alumno.fecha_ultimo_pago,
        "estado": alumno.estado_pago,
        "dias_desde_ultimo_pago": (date.today() - alumno.fecha_ultimo_pago).days
    }

@router.get("/{alumno_id}/inscripciones-clase", response_model=List[InscripcionClaseResponse])
def obtener_inscripciones_clase_alumno(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    """Obtener todas las inscripciones del alumno a clases"""
    
    # Verificar que el alumno existe
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    inscripciones = db.query(InscripcionClaseDB).filter(
        InscripcionClaseDB.alumno_id == alumno_id,
        InscripcionClaseDB.activo == True
    ).all()
    
    resultados = []
    for ins in inscripciones:
        resultados.append({
            "id": ins.id,
            "alumno_id": ins.alumno_id,
            "horario_id": ins.horario_id,
            "activo": ins.activo,
            "fecha_inscripcion": ins.fecha_inscripcion,
            "notas": ins.notas,
            "alumno_nombre": f"{alumno.nombre} {alumno.apellidos}"
        })
    
    return resultados