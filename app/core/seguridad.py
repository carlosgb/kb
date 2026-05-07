# app/core/seguridad.py
"""Dependencias de seguridad para proteger rutas"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.auth import decode_access_token
from app.models.usuario import UsuarioDB

# Esquema de seguridad para Bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UsuarioDB:
    """Obtiene el usuario actual a partir del token"""
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(UsuarioDB).filter(UsuarioDB.username == username, UsuarioDB.activo == True).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: UsuarioDB = Depends(get_current_user),
) -> UsuarioDB:
    """Verifica que el usuario esté activo"""
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


# Funciones para verificar roles
def require_role(roles: list):
    """Decorador para requerir roles específicos"""
    async def role_checker(current_user: UsuarioDB = Depends(get_current_active_user)):
        if current_user.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de estos roles: {', '.join(roles)}"
            )
        return current_user
    return role_checker


# Dependencias específicas por rol
def require_admin(current_user: UsuarioDB = Depends(get_current_active_user)):
    """Requiere rol de administrador"""
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador"
        )
    return current_user


def require_maestro(current_user: UsuarioDB = Depends(get_current_active_user)):
    """Requiere rol de maestro o admin"""
    if current_user.rol not in ["admin", "maestro"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de maestro o administrador"
        )
    return current_user


def require_recepcion(current_user: UsuarioDB = Depends(get_current_active_user)):
    """Requiere rol de recepción, maestro o admin"""
    if current_user.rol not in ["admin", "maestro", "recepcion"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a este recurso"
        )
    return current_user


# Dependencia opcional (para rutas que pueden estar autenticadas o no)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[UsuarioDB]:
    """Obtiene el usuario si el token es válido, sino None"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username:
            user = db.query(UsuarioDB).filter(UsuarioDB.username == username, UsuarioDB.activo == True).first()
            return user
    except:
        pass
    
    return None