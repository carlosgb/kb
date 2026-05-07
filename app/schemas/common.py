# app/schemas/common.py
"""Esquemas comunes reutilizables"""

from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class MessageResponse(BaseModel):
    """Respuesta simple con mensaje"""
    message: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """Respuesta de error"""
    error: str
    detail: Optional[str] = None
    status_code: int

class PaginationParams(BaseModel):
    """Parámetros de paginación"""
    page: int = Field(1, ge=1, description="Número de página")
    page_size: int = Field(20, ge=1, le=100, description="Elementos por página")
    order_by: Optional[str] = Field(None, description="Campo para ordenar")
    order_desc: bool = Field(False, description="Orden descendente")

class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada genérica"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams):
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size
        )

class DateRangeFilter(BaseModel):
    """Filtro por rango de fechas"""
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None

class IdNameResponse(BaseModel):
    """Respuesta simple con ID y nombre"""
    id: int
    nombre: str
    
    class Config:
        from_attributes = True