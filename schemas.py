from pydantic import BaseModel
from typing import List

class UsuarioBase(BaseModel):
    nombre: str
    contrasena: str
    cedula: int
    direccion: str
    correo: str
    telefono: int
    ciudad: str
    departamento: str
    ubicacion_geografica: str
    estado: str
    fecha_de_corte: str
    rol: str

class UsuarioUpdate(UsuarioBase):
    pass


class UsuarioCreate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id_usuario: int

    class Config:
        orm_mode = True

class PlanBase(BaseModel):
    tipo_de_plan: str
    precio: int
    megas: str
    tiempo_de_contrato: str
    numero_de_routes: int
    numero_de_decodificadores: int
    id_usuario: int

class PlanCreate(BaseModel):
    tipo_de_plan: str
    precio: int
    megas: str
    tiempo_de_contrato: str
    numero_de_routes: int
    numero_de_decodificadores: int
    id_usuario: int

class Plan(BaseModel):
    id_plan: int
    tipo_de_plan: str
    precio: int
    megas: str 
    tiempo_de_contrato: str
    numero_de_routes: int
    numero_de_decodificadores: int
    id_usuario: int

    class Config:
        orm_mode = True

class PlanUpdate(BaseModel):
    tipo_de_plan: str
    precio: int
    megas: int
    tiempo_de_contrato: str
    numero_de_routes: int
    numero_de_decodificadores: int
    id_usuario: int

class LoginData(BaseModel):
    nombre: str
    contrasena: str
   

