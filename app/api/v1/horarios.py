# app/api/v1/horarios.py
"""Endpoints para gestión de horarios de clases"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime

from app.core.database import get_db
from app.models import (
    HorarioClaseDB, InscripcionClaseDB, AlumnoDB, MaestroDB
)
from app.schemas import (
    HorarioClaseCreate, HorarioClaseUpdate, HorarioClaseResponse,
    InscripcionClaseCreate, InscripcionClaseResponse,
    MessageResponse
)

router = APIRouter()


# ==================== CRUD HORARIOS ====================

@router.post("/", response_model=HorarioClaseResponse, status_code=status.HTTP_201_CREATED)
def crear_horario(
    horario: HorarioClaseCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo horario de clase"""
    
    # Validar que el horario no se solape con otro del mismo maestro
    if horario.maestro_id:
        overlapping = db.query(HorarioClaseDB).filter(
            HorarioClaseDB.maestro_id == horario.maestro_id,
            HorarioClaseDB.dia_semana == horario.dia_semana,
            HorarioClaseDB.hora_inicio < horario.hora_fin,
            HorarioClaseDB.hora_fin > horario.hora_inicio,
            HorarioClaseDB.activo == True
        ).first()
        
        if overlapping:
            raise HTTPException(
                status_code=400, 
                detail=f"El maestro ya tiene una clase en ese horario: {overlapping.nombre}"
            )
    
    # Calcular duración en minutos
    h1, m1 = map(int, horario.hora_inicio.split(':'))
    h2, m2 = map(int, horario.hora_fin.split(':'))
    duracion = (h2 * 60 + m2) - (h1 * 60 + m1)
    if duracion < 0:
        duracion += 24 * 60
    
    # Convertir el objeto Pydantic a diccionario
    horario_dict = horario.model_dump()
    horario_dict['duracion_minutos'] = duracion
    
    db_horario = HorarioClaseDB(**horario_dict)
    db.add(db_horario)
    db.commit()
    db.refresh(db_horario)
    
    # Obtener el nombre del maestro para la respuesta
    maestro_nombre = None
    if db_horario.maestro_id:
        maestro = db.query(MaestroDB).filter(MaestroDB.id == db_horario.maestro_id).first()
        if maestro:
            maestro_nombre = f"{maestro.nombre} {maestro.apellidos}"
    
    # Construir respuesta manualmente
    return {
        "id": db_horario.id,
        "nombre": db_horario.nombre,
        "tipo_clase": db_horario.tipo_clase,
        "nivel": db_horario.nivel,
        "dia_semana": db_horario.dia_semana,
        "hora_inicio": db_horario.hora_inicio,
        "hora_fin": db_horario.hora_fin,
        "capacidad_maxima": db_horario.capacidad_maxima,
        "salon": db_horario.salon,
        "maestro_id": db_horario.maestro_id,
        "activo": db_horario.activo,
        "duracion_minutos": db_horario.duracion_minutos,
        "alumnos_inscritos": 0,
        "lugares_disponibles": db_horario.capacidad_maxima,
        "esta_lleno": False,
        "dia_nombre": get_dia_nombre(db_horario.dia_semana),
        "horario_texto": f"{db_horario.hora_inicio} - {db_horario.hora_fin}",
        "maestro_nombre": maestro_nombre
    }


@router.get("/", response_model=List[HorarioClaseResponse])
def listar_horarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    dia_semana: Optional[int] = Query(None, ge=0, le=6),
    tipo_clase: Optional[str] = None,
    nivel: Optional[str] = None,
    maestro_id: Optional[int] = None,
    activo: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Listar horarios de clase con filtros"""
    
    query = db.query(HorarioClaseDB)
    
    if dia_semana is not None:
        query = query.filter(HorarioClaseDB.dia_semana == dia_semana)
    if tipo_clase:
        query = query.filter(HorarioClaseDB.tipo_clase == tipo_clase)
    if nivel:
        query = query.filter(HorarioClaseDB.nivel == nivel)
    if maestro_id:
        query = query.filter(HorarioClaseDB.maestro_id == maestro_id)
    if activo is not None:
        query = query.filter(HorarioClaseDB.activo == activo)
    
    horarios = query.order_by(
        HorarioClaseDB.dia_semana, 
        HorarioClaseDB.hora_inicio
    ).offset(skip).limit(limit).all()
    
    # Construir respuesta manualmente sin asignar propiedades
    resultados = []
    for h in horarios:
        # Contar inscripciones activas
        inscritos_activos = db.query(InscripcionClaseDB).filter(
            InscripcionClaseDB.horario_id == h.id,
            InscripcionClaseDB.activo == True
        ).count()
        
        # Obtener nombre del maestro
        maestro_nombre = None
        if h.maestro_id:
            maestro = db.query(MaestroDB).filter(MaestroDB.id == h.maestro_id).first()
            if maestro:
                maestro_nombre = f"{maestro.nombre} {maestro.apellidos}"
        
        resultados.append({
            "id": h.id,
            "nombre": h.nombre,
            "tipo_clase": h.tipo_clase,
            "nivel": h.nivel,
            "dia_semana": h.dia_semana,
            "hora_inicio": h.hora_inicio,
            "hora_fin": h.hora_fin,
            "capacidad_maxima": h.capacidad_maxima,
            "salon": h.salon,
            "maestro_id": h.maestro_id,
            "activo": h.activo,
            "duracion_minutos": h.duracion_minutos,
            "alumnos_inscritos": inscritos_activos,
            "lugares_disponibles": h.capacidad_maxima - inscritos_activos,
            "esta_lleno": inscritos_activos >= h.capacidad_maxima,
            "dia_nombre": get_dia_nombre(h.dia_semana),
            "horario_texto": f"{h.hora_inicio} - {h.hora_fin}",
            "maestro_nombre": maestro_nombre
        })
    
    return resultados


def get_dia_nombre(dia_numero):
    """Convierte número de día a nombre"""
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[dia_numero] if 0 <= dia_numero < 7 else "Desconocido"


@router.get("/disponibles", response_model=List[HorarioClaseResponse])
def horarios_con_cupo(
    dia_semana: Optional[int] = Query(None, ge=0, le=6),
    db: Session = Depends(get_db)
):
    """Listar horarios que tienen cupo disponible"""
    
    query = db.query(HorarioClaseDB).filter(HorarioClaseDB.activo == True)
    
    if dia_semana is not None:
        query = query.filter(HorarioClaseDB.dia_semana == dia_semana)
    
    horarios = query.all()
    
    resultados = []
    for h in horarios:
        inscritos_activos = db.query(InscripcionClaseDB).filter(
            InscripcionClaseDB.horario_id == h.id,
            InscripcionClaseDB.activo == True
        ).count()
        
        if inscritos_activos < h.capacidad_maxima:
            maestro_nombre = None
            if h.maestro_id:
                maestro = db.query(MaestroDB).filter(MaestroDB.id == h.maestro_id).first()
                if maestro:
                    maestro_nombre = f"{maestro.nombre} {maestro.apellidos}"
            
            resultados.append({
                "id": h.id,
                "nombre": h.nombre,
                "tipo_clase": h.tipo_clase,
                "nivel": h.nivel,
                "dia_semana": h.dia_semana,
                "hora_inicio": h.hora_inicio,
                "hora_fin": h.hora_fin,
                "capacidad_maxima": h.capacidad_maxima,
                "salon": h.salon,
                "maestro_id": h.maestro_id,
                "activo": h.activo,
                "duracion_minutos": h.duracion_minutos,
                "alumnos_inscritos": inscritos_activos,
                "lugares_disponibles": h.capacidad_maxima - inscritos_activos,
                "esta_lleno": False,
                "dia_nombre": get_dia_nombre(h.dia_semana),
                "horario_texto": f"{h.hora_inicio} - {h.hora_fin}",
                "maestro_nombre": maestro_nombre
            })
    
    return resultados


@router.get("/hoy", response_model=List[HorarioClaseResponse])
def horarios_hoy(
    db: Session = Depends(get_db)
):
    """Obtener todos los horarios de hoy"""
    
    dia_hoy = datetime.now().weekday()
    
    horarios = db.query(HorarioClaseDB).filter(
        HorarioClaseDB.dia_semana == dia_hoy,
        HorarioClaseDB.activo == True
    ).order_by(HorarioClaseDB.hora_inicio).all()
    
    resultados = []
    for h in horarios:
        inscritos_activos = db.query(InscripcionClaseDB).filter(
            InscripcionClaseDB.horario_id == h.id,
            InscripcionClaseDB.activo == True
        ).count()
        
        maestro_nombre = None
        if h.maestro_id:
            maestro = db.query(MaestroDB).filter(MaestroDB.id == h.maestro_id).first()
            if maestro:
                maestro_nombre = f"{maestro.nombre} {maestro.apellidos}"
        
        resultados.append({
            "id": h.id,
            "nombre": h.nombre,
            "tipo_clase": h.tipo_clase,
            "nivel": h.nivel,
            "dia_semana": h.dia_semana,
            "hora_inicio": h.hora_inicio,
            "hora_fin": h.hora_fin,
            "capacidad_maxima": h.capacidad_maxima,
            "salon": h.salon,
            "maestro_id": h.maestro_id,
            "activo": h.activo,
            "duracion_minutos": h.duracion_minutos,
            "alumnos_inscritos": inscritos_activos,
            "lugares_disponibles": h.capacidad_maxima - inscritos_activos,
            "esta_lleno": inscritos_activos >= h.capacidad_maxima,
            "dia_nombre": get_dia_nombre(h.dia_semana),
            "horario_texto": f"{h.hora_inicio} - {h.hora_fin}",
            "maestro_nombre": maestro_nombre
        })
    
    return resultados


@router.get("/{horario_id}", response_model=HorarioClaseResponse)
def obtener_horario(
    horario_id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalles de un horario"""
    
    horario = db.query(HorarioClaseDB).filter(HorarioClaseDB.id == horario_id).first()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    inscritos_activos = db.query(InscripcionClaseDB).filter(
        InscripcionClaseDB.horario_id == horario_id,
        InscripcionClaseDB.activo == True
    ).count()
    
    maestro_nombre = None
    if horario.maestro_id:
        maestro = db.query(MaestroDB).filter(MaestroDB.id == horario.maestro_id).first()
        if maestro:
            maestro_nombre = f"{maestro.nombre} {maestro.apellidos}"
    
    return {
        "id": horario.id,
        "nombre": horario.nombre,
        "tipo_clase": horario.tipo_clase,
        "nivel": horario.nivel,
        "dia_semana": horario.dia_semana,
        "hora_inicio": horario.hora_inicio,
        "hora_fin": horario.hora_fin,
        "capacidad_maxima": horario.capacidad_maxima,
        "salon": horario.salon,
        "maestro_id": horario.maestro_id,
        "activo": horario.activo,
        "duracion_minutos": horario.duracion_minutos,
        "alumnos_inscritos": inscritos_activos,
        "lugares_disponibles": horario.capacidad_maxima - inscritos_activos,
        "esta_lleno": inscritos_activos >= horario.capacidad_maxima,
        "dia_nombre": get_dia_nombre(horario.dia_semana),
        "horario_texto": f"{horario.hora_inicio} - {horario.hora_fin}",
        "maestro_nombre": maestro_nombre
    }


@router.put("/{horario_id}", response_model=HorarioClaseResponse)
def actualizar_horario(
    horario_id: int,
    horario_update: HorarioClaseUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un horario"""
    
    horario = db.query(HorarioClaseDB).filter(HorarioClaseDB.id == horario_id).first()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    update_data = horario_update.model_dump(exclude_unset=True)
    
    # Si cambió el horario, recalcular duración
    if 'hora_inicio' in update_data or 'hora_fin' in update_data:
        hora_inicio = update_data.get('hora_inicio', horario.hora_inicio)
        hora_fin = update_data.get('hora_fin', horario.hora_fin)
        h1, m1 = map(int, hora_inicio.split(':'))
        h2, m2 = map(int, hora_fin.split(':'))
        duracion = (h2 * 60 + m2) - (h1 * 60 + m1)
        if duracion < 0:
            duracion += 24 * 60
        update_data['duracion_minutos'] = duracion
    
    for field, value in update_data.items():
        setattr(horario, field, value)
    
    db.commit()
    db.refresh(horario)
    
    inscritos_activos = db.query(InscripcionClaseDB).filter(
        InscripcionClaseDB.horario_id == horario_id,
        InscripcionClaseDB.activo == True
    ).count()
    
    maestro_nombre = None
    if horario.maestro_id:
        maestro = db.query(MaestroDB).filter(MaestroDB.id == horario.maestro_id).first()
        if maestro:
            maestro_nombre = f"{maestro.nombre} {maestro.apellidos}"
    
    return {
        "id": horario.id,
        "nombre": horario.nombre,
        "tipo_clase": horario.tipo_clase,
        "nivel": horario.nivel,
        "dia_semana": horario.dia_semana,
        "hora_inicio": horario.hora_inicio,
        "hora_fin": horario.hora_fin,
        "capacidad_maxima": horario.capacidad_maxima,
        "salon": horario.salon,
        "maestro_id": horario.maestro_id,
        "activo": horario.activo,
        "duracion_minutos": horario.duracion_minutos,
        "alumnos_inscritos": inscritos_activos,
        "lugares_disponibles": horario.capacidad_maxima - inscritos_activos,
        "esta_lleno": inscritos_activos >= horario.capacidad_maxima,
        "dia_nombre": get_dia_nombre(horario.dia_semana),
        "horario_texto": f"{horario.hora_inicio} - {horario.hora_fin}",
        "maestro_nombre": maestro_nombre
    }


@router.delete("/{horario_id}", response_model=MessageResponse)
def eliminar_horario(
    horario_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar (desactivar) un horario"""
    
    horario = db.query(HorarioClaseDB).filter(HorarioClaseDB.id == horario_id).first()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    horario.activo = False
    db.commit()
    
    return MessageResponse(message="Horario desactivado correctamente")


# ==================== INSCRIPCIONES A CLASES ====================

@router.post("/{horario_id}/inscribir", response_model=InscripcionClaseResponse)
def inscribir_alumno_clase(
    horario_id: int,
    inscripcion: InscripcionClaseCreate,
    alumno_id: int = Query(..., description="ID del alumno"),
    db: Session = Depends(get_db)
):
    """Inscribir un alumno a una clase recurrente"""
    
    # Verificar horario
    horario = db.query(HorarioClaseDB).filter(HorarioClaseDB.id == horario_id).first()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    # Verificar cupo
    inscritos_actuales = db.query(InscripcionClaseDB).filter(
        InscripcionClaseDB.horario_id == horario_id,
        InscripcionClaseDB.activo == True
    ).count()
    
    if inscritos_actuales >= horario.capacidad_maxima:
        raise HTTPException(status_code=400, detail="El horario ya está lleno")
    
    # Verificar alumno
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Verificar no duplicado
    existing = db.query(InscripcionClaseDB).filter(
        InscripcionClaseDB.horario_id == horario_id,
        InscripcionClaseDB.alumno_id == alumno_id,
        InscripcionClaseDB.activo == True
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Alumno ya inscrito en esta clase")
    
    db_inscripcion = InscripcionClaseDB(
        horario_id=horario_id,
        alumno_id=alumno_id,
        notas=inscripcion.notas if hasattr(inscripcion, 'notas') else None
    )
    
    db.add(db_inscripcion)
    db.commit()
    db.refresh(db_inscripcion)
    
    return db_inscripcion


@router.get("/{horario_id}/inscritos", response_model=List[InscripcionClaseResponse])
def listar_inscritos_clase(
    horario_id: int,
    solo_activos: bool = True,
    db: Session = Depends(get_db)
):
    """Listar alumnos inscritos en una clase"""
    
    query = db.query(InscripcionClaseDB).filter(
        InscripcionClaseDB.horario_id == horario_id
    )
    
    if solo_activos:
        query = query.filter(InscripcionClaseDB.activo == True)
    
    inscritos = query.all()
    
    # Agregar información del alumno
    resultados = []
    for i in inscritos:
        alumno = db.query(AlumnoDB).filter(AlumnoDB.id == i.alumno_id).first()
        resultados.append({
            "id": i.id,
            "alumno_id": i.alumno_id,
            "horario_id": i.horario_id,
            "activo": i.activo,
            "fecha_inscripcion": i.fecha_inscripcion,
            "alumno_nombre": f"{alumno.nombre} {alumno.apellidos}" if alumno else None
        })
    
    return resultados


@router.delete("/inscripciones/{inscripcion_id}", response_model=MessageResponse)
def dar_baja_clase(
    inscripcion_id: int,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Dar de baja a un alumno de una clase"""
    
    inscripcion = db.query(InscripcionClaseDB).filter(
        InscripcionClaseDB.id == inscripcion_id
    ).first()
    
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    
    inscripcion.activo = False
    inscripcion.fecha_baja = date.today()
    if motivo:
        inscripcion.notas = motivo if inscripcion.notas else f"Baja: {motivo}"
    
    db.commit()
    
    return MessageResponse(message="Alumno dado de baja de la clase", details=motivo)