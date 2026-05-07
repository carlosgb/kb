# app/api/v1/seguros.py
"""Endpoints para gestión de seguros médicos"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta
import uuid

from app.core.database import get_db
from app.models import (
    AseguradoraDB, PolizaSeguroDB, ContratoSeguroDB, 
    SiniestroSeguroDB, AlumnoDB
)
from app.schemas import (
    AseguradoraResponse, AseguradoraCreate,
    PolizaSeguroResponse, PolizaSeguroCreate,
    ContratoSeguroCreate, ContratoSeguroResponse,
    SiniestroSeguroCreate, SiniestroSeguroResponse,
    MessageResponse
)

router = APIRouter()


# ==================== ASEGURADORAS ====================

@router.post("/aseguradoras", response_model=AseguradoraResponse, status_code=status.HTTP_201_CREATED)
def crear_aseguradora(
    aseguradora: AseguradoraCreate,
    db: Session = Depends(get_db)
):
    """Registrar una aseguradora"""
    
    existing = db.query(AseguradoraDB).filter(AseguradoraDB.nombre == aseguradora.nombre).first()
    if existing:
        raise HTTPException(status_code=400, detail="Aseguradora ya existe")
    
    db_aseguradora = AseguradoraDB(**aseguradora.model_dump())
    db.add(db_aseguradora)
    db.commit()
    db.refresh(db_aseguradora)
    
    return db_aseguradora


@router.get("/aseguradoras", response_model=List[AseguradoraResponse])
def listar_aseguradoras(
    activo: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Listar aseguradoras"""
    
    query = db.query(AseguradoraDB)
    if activo is not None:
        query = query.filter(AseguradoraDB.activo == activo)
    
    return query.all()


# ==================== PÓLIZAS ====================

@router.post("/polizas", response_model=PolizaSeguroResponse, status_code=status.HTTP_201_CREATED)
def crear_poliza(
    poliza: PolizaSeguroCreate,
    db: Session = Depends(get_db)
):
    """Registrar una póliza de seguro"""
    
    aseguradora = db.query(AseguradoraDB).filter(AseguradoraDB.id == poliza.aseguradora_id).first()
    if not aseguradora:
        raise HTTPException(status_code=404, detail="Aseguradora no encontrada")
    
    db_poliza = PolizaSeguroDB(**poliza.model_dump())
    db.add(db_poliza)
    db.commit()
    db.refresh(db_poliza)
    
    return db_poliza


@router.get("/polizas", response_model=List[PolizaSeguroResponse])
def listar_polizas(
    aseguradora_id: Optional[int] = None,
    activa: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Listar pólizas con filtros"""
    
    query = db.query(PolizaSeguroDB)
    
    if aseguradora_id:
        query = query.filter(PolizaSeguroDB.aseguradora_id == aseguradora_id)
    if activa is not None:
        query = query.filter(PolizaSeguroDB.activa == activa)
    
    return query.all()


# ==================== CONTRATOS DE SEGURO ====================

@router.post("/alumnos/{alumno_id}/contratar", response_model=ContratoSeguroResponse)
def contratar_seguro(
    alumno_id: int,
    contrato: ContratoSeguroCreate,
    db: Session = Depends(get_db)
):
    """Contratar un seguro para un alumno"""
    
    # Verificar alumno
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Verificar póliza
    poliza = db.query(PolizaSeguroDB).filter(PolizaSeguroDB.id == contrato.poliza_id).first()
    if not poliza:
        raise HTTPException(status_code=404, detail="Póliza no encontrada")
    
    # Validar que la póliza esté vigente
    if not poliza.vigente:
        raise HTTPException(status_code=400, detail="La póliza no está vigente en estas fechas")
    
    # Generar número de certificado único
    numero_certificado = f"CERT-{alumno_id}-{uuid.uuid4().hex[:8].upper()}"
    
    db_contrato = ContratoSeguroDB(
        alumno_id=alumno_id,
        numero_certificado=numero_certificado,
        **contrato.model_dump()
    )
    
    db.add(db_contrato)
    db.commit()
    db.refresh(db_contrato)
    
    return db_contrato


@router.get("/alumnos/{alumno_id}/seguros", response_model=List[ContratoSeguroResponse])
def obtener_seguros_alumno(
    alumno_id: int,
    solo_activos: bool = True,
    db: Session = Depends(get_db)
):
    """Obtener todos los seguros de un alumno"""
    
    query = db.query(ContratoSeguroDB).filter(ContratoSeguroDB.alumno_id == alumno_id)
    
    if solo_activos:
        query = query.filter(ContratoSeguroDB.activo == True)
    
    seguros = query.order_by(ContratoSeguroDB.fecha_inicio.desc()).all()
    return seguros


@router.get("/alumnos/{alumno_id}/seguro-activo", response_model=ContratoSeguroResponse)
def obtener_seguro_activo(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    """Obtener el seguro activo del alumno"""
    
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    seguro = alumno.seguro_activo
    if not seguro:
        raise HTTPException(status_code=404, detail="No hay seguro activo")
    
    return seguro


# ==================== SINIESTROS ====================

@router.post("/siniestros", response_model=SiniestroSeguroResponse)
def reportar_siniestro(
    siniestro: SiniestroSeguroCreate,
    db: Session = Depends(get_db)
):
    """Reportar un accidente/lesión para reclamo al seguro"""
    
    # Verificar contrato
    contrato = db.query(ContratoSeguroDB).filter(ContratoSeguroDB.id == siniestro.contrato_id).first()
    if not contrato or not contrato.vigente:
        raise HTTPException(status_code=404, detail="Contrato no encontrado o no vigente")
    
    # Generar número de siniestro
    numero_siniestro = f"SIN-{siniestro.contrato_id}-{uuid.uuid4().hex[:8].upper()}"
    
    db_siniestro = SiniestroSeguroDB(
        numero_siniestro=numero_siniestro,
        estado="Reportado",
        **siniestro.model_dump()
    )
    
    db.add(db_siniestro)
    db.commit()
    db.refresh(db_siniestro)
    
    return db_siniestro


@router.get("/siniestros/{siniestro_id}", response_model=SiniestroSeguroResponse)
def obtener_siniestro(
    siniestro_id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalles de un siniestro"""
    
    siniestro = db.query(SiniestroSeguroDB).filter(SiniestroSeguroDB.id == siniestro_id).first()
    if not siniestro:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")
    
    return siniestro


@router.put("/siniestros/{siniestro_id}/estado", response_model=SiniestroSeguroResponse)
def actualizar_estado_siniestro(
    siniestro_id: int,
    estado: str,
    monto_cubierto: Optional[float] = None,
    fecha_resolucion: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Actualizar estado de un siniestro"""
    
    estados_validos = ["Reportado", "En proceso", "Aprobado", "Rechazado", "Pagado"]
    if estado not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Opciones: {estados_validos}")
    
    siniestro = db.query(SiniestroSeguroDB).filter(SiniestroSeguroDB.id == siniestro_id).first()
    if not siniestro:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")
    
    siniestro.estado = estado
    if monto_cubierto is not None:
        siniestro.monto_cubierto = monto_cubierto
    if fecha_resolucion:
        siniestro.fecha_resolucion = fecha_resolucion
    if estado == "Pagado":
        siniestro.fecha_pago = date.today()
    
    db.commit()
    db.refresh(siniestro)
    
    return siniestro


@router.get("/alumnos/{alumno_id}/siniestros", response_model=List[SiniestroSeguroResponse])
def obtener_siniestros_alumno(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    """Obtener todos los siniestros de un alumno"""
    
    siniestros = db.query(SiniestroSeguroDB).join(
        ContratoSeguroDB
    ).filter(
        ContratoSeguroDB.alumno_id == alumno_id
    ).all()
    
    return siniestros


# ==================== REPORTES ====================

@router.get("/reportes/vencimientos", response_model=List[dict])
def seguros_por_vencer(
    dias: int = Query(30, ge=1, le=180),
    db: Session = Depends(get_db)
):
    """Reporte de seguros que vencen en los próximos X días"""
    
    hoy = date.today()
    fecha_limite = hoy + timedelta(days=dias)
    
    contratos = db.query(ContratoSeguroDB).filter(
        ContratoSeguroDB.activo == True,
        ContratoSeguroDB.fecha_fin <= fecha_limite,
        ContratoSeguroDB.fecha_fin >= hoy
    ).all()
    
    return [
        {
            "alumno": f"{c.alumno.nombre} {c.alumno.apellidos}",
            "aseguradora": c.poliza.aseguradora.nombre,
            "plan": c.poliza.nombre_plan,
            "numero_certificado": c.numero_certificado,
            "vencimiento": c.fecha_fin,
            "dias_restantes": c.dias_restantes
        }
        for c in contratos
    ]