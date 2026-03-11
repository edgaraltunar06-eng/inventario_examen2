from pydantic import BaseModel
from typing import Optional
class Producto(BaseModel):
    nombre: str
    precio: float
    stock: int