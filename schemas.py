from pydantic import BaseModel
from typing import Optional

#este esquema va a validar los datos que llegan desde el frontend 

class ProductoNuevo(BaseModel):
    nombre: str
    descripcion: Optional[str] = None #que lleve optional significa que puede quedar vacio
    precio: float
    stock: int
    url_imagen: Optional[str] = None

    class Config:
        from_attributes = True


class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    contrasena: str


class UsuarioLogin(BaseModel):
    email: str
    contrasena: str


class NuevaCompra(BaseModel):
    id_usuario: int
    id_producto: int
    cantidad: int