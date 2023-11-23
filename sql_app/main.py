from typing import Optional
from fastapi import FastAPI, Request, Header, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, schemas, crud 

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


templates = Jinja2Templates(directory="sql_app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/mechanics/", response_model=schemas.Mechanic)
def create_mechanic(mechanic: schemas.MechanicCreate, db: Session = Depends(get_db)):
    db_mechanic = crud.get_mechanic_by_login(db, login=mechanic.login) 
    if db_mechanic:
        raise HTTPException(status_code=400, detail="Login już istnieje")
    return crud.create_mechanic(db=db, mechanic=mechanic)


@app.get("/mechanics/", response_model=list[schemas.Mechanic])
def read_mechanics(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    mechanics = crud.get_mechanics(db, skip=skip, limit=limit)
    context = {"request": request, "mechanics": mechanics}
    return templates.TemplateResponse("mechanics.html", context)


@app.get("/create_mechanic/")
def create_mechanic_form(request: Request, db: Session = Depends(get_db)):
    context = {"request": request}
    return templates.TemplateResponse("create_mechanic.html", context)
