# app/api/v1/auth.py
"""Endpoints de autenticación"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from app.core.database import get_db
from app.core.auth import verify_password, get_password_hash, create_access_token
from app.core.seguridad import get_current_active_user, require_admin
from app.models.usuario import UsuarioDB
from app.schemas.usuario import (
    UsuarioCreate, UsuarioResponse, UsuarioUpdate,
    LoginRequest, LoginResponse, ChangePasswordRequest
)

router = APIRouter(tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    admin: UsuarioDB = Depends(require_admin)  # Solo admin puede crear usuarios
):
    """Registrar un nuevo usuario (solo administradores)"""
    
    # Verificar si el username ya existe
    existing_user = db.query(UsuarioDB).filter(UsuarioDB.username == usuario.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Nombre de usuario ya existe")
    
    # Verificar si el email ya existe
    existing_email = db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(usuario.password)
    
    db_usuario = UsuarioDB(
        username=usuario.username,
        email=usuario.email,
        hashed_password=hashed_password,
        nombre=usuario.nombre,
        apellidos=usuario.apellidos,
        telefono=usuario.telefono,
        rol=usuario.rol,
        activo=usuario.activo
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión"""
    
    # Buscar usuario por username o email
    user = db.query(UsuarioDB).filter(
        (UsuarioDB.username == request.username) | (UsuarioDB.email == request.username),
        UsuarioDB.activo == True
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar contraseña
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Actualizar último acceso
    user.ultimo_acceso = datetime.now()
    db.commit()
    
    # Crear token
    access_token = create_access_token(
        data={"sub": user.username, "rol": user.rol}
    )
    
    return LoginResponse(
        access_token=access_token,
        usuario=user
    )


@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: UsuarioDB = Depends(get_current_active_user)):
    """Obtener información del usuario autenticado"""
    return current_user


@router.put("/me/cambiar-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: UsuarioDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cambiar la contraseña del usuario actual"""
    
    # Verificar contraseña actual
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    # Actualizar contraseña
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Contraseña actualizada correctamente"}


@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def update_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: UsuarioDB = Depends(require_admin)
):
    """Actualizar un usuario (solo administradores)"""
    
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    update_data = usuario_update.model_dump(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    
    return usuario


@router.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: UsuarioDB = Depends(require_admin)
):
    """Listar todos los usuarios (solo administradores)"""
    usuarios = db.query(UsuarioDB).offset(skip).limit(limit).all()
    return usuarios


@router.delete("/usuarios/{usuario_id}")
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: UsuarioDB = Depends(require_admin)
):
    """Eliminar usuario (solo administradores)"""
    
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(usuario)
    db.commit()
    
    return {"message": "Usuario eliminado correctamente"}


@router.post("/logout")
def logout():
    """Cerrar sesión (el frontend debe eliminar el token)"""
    return {"message": "Sesión cerrada correctamente"}