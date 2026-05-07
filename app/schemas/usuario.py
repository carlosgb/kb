# app/schemas/usuario.py
"""Esquemas para autenticación y usuarios"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


class UsuarioBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nombre: str = Field(..., min_length=2, max_length=50)
    apellidos: str = Field(..., min_length=2, max_length=100)
    telefono: Optional[str] = None
    rol: str = Field("invitado", pattern="^(admin|maestro|recepcion|caja|invitado)$")
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None
    password: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id: int
    created_at: datetime
    ultimo_acceso: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)
    
    @field_validator('new_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('La nueva contraseña debe tener al menos 6 caracteres')
        return v


class TokenData(BaseModel):
    username: Optional[str] = None
    rol: Optional[str] = None