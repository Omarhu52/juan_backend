from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

server = "ESTEBANBARRERA\SQLEXPRESS"
dbname = "ACERONET"  

DATABASE_URL = f"mssql+pyodbc://{server}/{dbname}?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    contrasena = Column(String, nullable=False)
    cedula = Column(Integer, nullable=False)
    direccion = Column(String, nullable=False)
    correo = Column(String, nullable=False)
    telefono = Column(Integer, nullable=False)
    ciudad = Column(String, nullable=False)
    departamento = Column(String, nullable=False)
    ubicacion_geografica = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    fecha_de_corte = Column(String, nullable=False)
    rol=Column(String, nullable=False)
    planes = relationship("Plan", back_populates="usuario")

class Plan(Base):
    __tablename__ = "planes"
    id_plan = Column(Integer, primary_key=True, index=True)
    tipo_de_plan = Column(String, nullable=False)
    precio = Column(Integer, nullable=False)
    megas = Column(String, nullable=False)
    tiempo_de_contrato = Column(String, nullable=False)
    numero_de_routes = Column(Integer, nullable=False)
    numero_de_decodificadores = Column(Integer, nullable=False)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'))  # Cambiamos esto de usuario_id a id_usuario
    usuario = relationship("Usuario", back_populates="planes")

Base.metadata.create_all(bind=engine)
