from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas, hasher


def get_mechanic(db: Session, mechanic_id: int):
    return db.query(models.Mechanic).filter(models.Mechanic.id == mechanic_id).first()

def get_mechanic_by_login(db: Session, login: str):
    return db.query(models.Mechanic).filter(models.Mechanic.login == login).first()

def get_mechanics(db: Session):
    return db.query(models.Mechanic).all()


def create_mechanic(db: Session, mechanic:schemas.MechanicCreate):
    hashed_password = hasher.Hasher.get_password_hash(mechanic.password)
    db_mechanic = models.Mechanic(login=mechanic.login,first_name=mechanic.first_name,last_name=mechanic.last_name, hashed_password=hashed_password, is_admin=mechanic.is_admin)
    db.add(db_mechanic)
    db.commit()
    db.refresh(db_mechanic)
    return db_mechanic

def delete_mechanic(db: Session, mechanic_id: int):
    db_mechanic = db.get(models.Mechanic, mechanic_id)
    if not db_mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    db.delete(db_mechanic)
    db.commit()


def create_repair(db: Session, repair: schemas.RepairCreate):
    db_repair = models.Repair(**repair.model_dump())
    db.add(db_repair)
    db.commit()
    db.refresh(db_repair)
    return db_repair

def get_repairs(db: Session):
    return db.query(models.Repair).all()


def get_repair(db: Session, repair_id: int):
    return db.query(models.Repair).filter(models.Repair.id == repair_id).first()
