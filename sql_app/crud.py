from sqlalchemy.orm import Session

from . import models, schemas


def get_mechanic(db: Session, mechanic_id: int):
    return db.query(models.Mechanic).filter(models.Mechanic.id == mechanic_id).first()

def get_mechanic_by_login(db: Session, login: str):
    return db.query(models.Mechanic).filter(models.Mechanic.login == login).first()

def get_mechanics(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Mechanic).offset(skip).limit(limit).all()


def create_mechanic(db: Session, mechanic:schemas.MechanicCreate):
    fake_hashed_password = mechanic.password + "notreallyhashed"
    db_mechanic = models.Mechanic(login=mechanic.login, hashed_password=fake_hashed_password, is_admin=mechanic.is_admin)
    db.add(db_mechanic)
    db.commit()
    db.refresh(db_mechanic)
    return db_mechanic


