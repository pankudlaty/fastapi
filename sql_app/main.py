from typing import Optional
from fastapi import FastAPI, Request, Header, Depends, HTTPException, Form, responses, status
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


@app.post("/create_mechanic/")
def create_mechanic( login: str = Form(...),first_name: str = Form(...), last_name: str = Form(...),password: str = Form(...),  db: Session = Depends(get_db)):
    mechanic = schemas.MechanicCreate(login=login,password=password,first_name=first_name, last_name=last_name, is_admin=False)
    crud.create_mechanic(db=db,mechanic=mechanic)
    return responses.RedirectResponse("/create_mechanic", status_code=status.HTTP_302_FOUND)

@app.get("/mechanics/", response_model=list[schemas.Mechanic])
def read_mechanics(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    mechanics = crud.get_mechanics(db, skip=skip, limit=limit)
    context = {"request": request, "mechanics": mechanics}
    return templates.TemplateResponse("mechanics.html", context)


@app.get("/create_mechanic/")
def create_mechanic_form(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("create_mechanic.html", context)


@app.delete("/delete_mechanic/{mechanic_id}")
def delete_mechanic(mechanic_id: int, db: Session = Depends(get_db)):
    return crud.delete_mechanic(db=db,mechanic_id=mechanic_id)
