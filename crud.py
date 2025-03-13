from sqlalchemy.orm import Session
import models, schemas
from models import Usuario, Plan
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

def get_usuario_by_nombre(db: Session, nombre: str):
    return db.query(Usuario).filter(Usuario.nombre == nombre).first()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
    db_usuario = Usuario(**usuario.dict())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def get_usuario(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()

def get_usuario_cedula(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.cedula == usuario_id).first()

def update_usuario(db: Session, usuario_id: int, usuario: schemas.UsuarioUpdate):
    db_usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    if db_usuario:
        for key, value in usuario.dict(exclude_unset=True).items():
            setattr(db_usuario, key, value)
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    else:
        return None


def delete_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.cedula == usuario_id).first()
    #usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    if usuario:
        for plan in usuario.planes:
            db.delete(plan)
        db.delete(usuario)
        db.commit()
        return JSONResponse(content={"message": "Usuario eliminado correctamente"}, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

def create_plan(db: Session, plan: schemas.PlanCreate):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.id_usuario == plan.id_usuario).first()
    if not usuario_existente:
        raise HTTPException(status_code=400, detail="El usuario especificado no existe")
    db_plan = Plan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_plan(db: Session, plan_id: int):
    return db.query(Plan).filter(Plan.id_plan == plan_id).first()

def update_plan(db: Session, plan_id: int, plan: schemas.PlanUpdate):
    db_plan = db.query(models.Plan).filter(models.Plan.id_plan == plan_id).first()
    if db_plan:
        for key, value in plan.dict().items():
            setattr(db_plan, key, value)
        db.commit()
        db.refresh(db_plan)
        return JSONResponse(content={"message": "Plan actualizado correctamente"}, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

def delete_plan(db: Session, plan_id: int):
    plan = db.query(Plan).filter(Plan.id_plan == plan_id).first()
    if plan:
        db.delete(plan)
        db.commit()
        return JSONResponse(content={"message": "Plan eliminado correctamente"}, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan no encontrado")    


def get_planes_by_usuario_id(db: Session, id_usuario: int):
    return db.query(Plan).filter(Plan.id_usuario == id_usuario).all()