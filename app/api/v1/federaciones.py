# app/api/v1/federaciones.py
"""Endpoints para gestión de federaciones y membresías"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta

from app.core.database import get_db
from app.models import (
    FederacionDB, CategoriaFederacionDB, MembresiaFederacionDB, AlumnoDB
)
from app.schemas import (
    FederacionCreate, FederacionResponse,
    CategoriaFederacionCreate, CategoriaFederacionResponse,
    MembresiaFederacionCreate, MembresiaFederacionResponse,
    MessageResponse
)

router = APIRouter()


# ==================== FEDERACIONES ====================

@router.post("/", response_model=FederacionResponse, status_code=status.HTTP_201_CREATED)
def crear_federacion(
    federacion: FederacionCreate,
    db: Session = Depends(get_db)
):
    """Registrar una nueva federación (WAKO, IFMA, ISKA, etc.)"""
    
    existing = db.query(FederacionDB).filter(FederacionDB.nombre == federacion.nombre).first()
    if existing:
        raise HTTPException(status_code=400, detail="Federación ya existe")
    
    db_federacion = FederacionDB(**federacion.model_dump())
    db.add(db_federacion)
    db.commit()
    db.refresh(db_federacion)
    
    return db_federacion


@router.get("/", response_model=List[FederacionResponse])
def listar_federaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    activo: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Listar todas las federaciones"""
    
    query = db.query(FederacionDB)
    
    if activo is not None:
        query = query.filter(FederacionDB.activo == activo)
    
    federaciones = query.offset(skip).limit(limit).all()
    return federaciones


@router.get("/{federacion_id}", response_model=FederacionResponse)
def obtener_federacion(
    federacion_id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalles de una federación"""
    
    federacion = db.query(FederacionDB).filter(FederacionDB.id == federacion_id).first()
    if not federacion:
        raise HTTPException(status_code=404, detail="Federación no encontrada")
    
    return federacion


@router.put("/{federacion_id}", response_model=FederacionResponse)
def actualizar_federacion(
    federacion_id: int,
    federacion_update: FederacionCreate,
    db: Session = Depends(get_db)
):
    """Actualizar datos de una federación"""
    
    federacion = db.query(FederacionDB).filter(FederacionDB.id == federacion_id).first()
    if not federacion:
        raise HTTPException(status_code=404, detail="Federación no encontrada")
    
    update_data = federacion_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(federacion, field, value)
    
    db.commit()
    db.refresh(federacion)
    
    return federacion


# ==================== CATEGORÍAS DE FEDERACIÓN ====================

@router.post("/{federacion_id}/categorias", response_model=CategoriaFederacionResponse)
def crear_categoria(
    federacion_id: int,
    categoria: CategoriaFederacionCreate,
    db: Session = Depends(get_db)
):
    """Crear una categoría para una federación"""
    
    federacion = db.query(FederacionDB).filter(FederacionDB.id == federacion_id).first()
    if not federacion:
        raise HTTPException(status_code=404, detail="Federación no encontrada")
    
    db_categoria = CategoriaFederacionDB(
        federacion_id=federacion_id,
        **categoria.model_dump()
    )
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    
    return db_categoria


@router.get("/{federacion_id}/categorias", response_model=List[CategoriaFederacionResponse])
def listar_categorias(
    federacion_id: int,
    activo: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Listar categorías de una federación"""
    
    query = db.query(CategoriaFederacionDB).filter(
        CategoriaFederacionDB.federacion_id == federacion_id
    )
    
    if activo is not None:
        query = query.filter(CategoriaFederacionDB.activo == activo)
    
    categorias = query.all()
    return categorias


# ==================== MEMBRESÍAS ====================

@router.post("/alumnos/{alumno_id}/membresia", response_model=MembresiaFederacionResponse)
def crear_membresia(
    alumno_id: int,
    membresia: MembresiaFederacionCreate,
    db: Session = Depends(get_db)
):
    """Crear membresía para un alumno en una federación"""
    
    # Verificar alumno
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Verificar federación
    federacion = db.query(FederacionDB).filter(FederacionDB.id == membresia.federacion_id).first()
    if not federacion:
        raise HTTPException(status_code=404, detail="Federación no encontrada")
    
    # Calcular fecha_fin si no se proporcionó
    if not membresia.fecha_fin:
        fecha_fin = membresia.fecha_inicio + timedelta(days=federacion.vigencia_dias)
    else:
        fecha_fin = membresia.fecha_fin
    
    db_membresia = MembresiaFederacionDB(
        alumno_id=alumno_id,
        fecha_fin=fecha_fin,
        **membresia.model_dump(exclude={'fecha_fin'})
    )
    
    db.add(db_membresia)
    db.commit()
    db.refresh(db_membresia)
    
    return db_membresia


@router.get("/alumnos/{alumno_id}/membresias", response_model=List[MembresiaFederacionResponse])
def obtener_membresias_alumno(
    alumno_id: int,
    solo_activas: bool = True,
    db: Session = Depends(get_db)
):
    """Obtener todas las membresías de un alumno"""
    
    query = db.query(MembresiaFederacionDB).filter(
        MembresiaFederacionDB.alumno_id == alumno_id
    )
    
    if solo_activas:
        query = query.filter(MembresiaFederacionDB.activa == True)
    
    membresias = query.order_by(MembresiaFederacionDB.fecha_inicio.desc()).all()
    return membresias


@router.put("/membresias/{membresia_id}/renovar", response_model=MembresiaFederacionResponse)
def renovar_membresia(
    membresia_id: int,
    costo: float,
    db: Session = Depends(get_db)
):
    """Renovar una membresía existente"""
    
    membresia = db.query(MembresiaFederacionDB).filter(
        MembresiaFederacionDB.id == membresia_id
    ).first()
    
    if not membresia:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    
    # Crear nueva membresía en lugar de actualizar (historial)
    nueva_fecha_inicio = date.today()
    nueva_fecha_fin = nueva_fecha_inicio + timedelta(days=membresia.federacion.vigencia_dias)
    
    nueva_membresia = MembresiaFederacionDB(
        alumno_id=membresia.alumno_id,
        federacion_id=membresia.federacion_id,
        numero_afiliacion=membresia.numero_afiliacion,  # Mismo número
        fecha_inicio=nueva_fecha_inicio,
        fecha_fin=nueva_fecha_fin,
        costo_pagado=costo,
        activa=True
    )
    
    # Desactivar la anterior
    membresia.activa = False
    membresia.fecha_cancelacion = date.today()
    
    db.add(nueva_membresia)
    db.commit()
    db.refresh(nueva_membresia)
    
    return nueva_membresia


@router.get("/reportes/vencimientos", response_model=List[dict])
def membresias_por_vencer(
    dias: int = Query(30, ge=1, le=180),
    db: Session = Depends(get_db)
):
    """Reporte de membresías que vencen en los próximos X días"""
    
    hoy = date.today()
    fecha_limite = hoy + timedelta(days=dias)
    
    membresias = db.query(MembresiaFederacionDB).filter(
        MembresiaFederacionDB.activa == True,
        MembresiaFederacionDB.fecha_fin <= fecha_limite,
        MembresiaFederacionDB.fecha_fin >= hoy
    ).all()
    
    return [
        {
            "alumno": f"{m.alumno.nombre} {m.alumno.apellidos}",
            "federacion": m.federacion.nombre,
            "numero_afiliacion": m.numero_afiliacion,
            "fecha_vencimiento": m.fecha_fin,
            "dias_restantes": m.dias_restantes
        }
        for m in membresias
    ]