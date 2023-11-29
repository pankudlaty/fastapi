from fastapi import FastAPI, Request, Depends,  Form, responses, status
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
def create_mechanic( login: str = Form(...),first_name: str = Form(...), last_name: str = Form(...),password: str = Form(...),is_admin: bool = Form(False),  db: Session = Depends(get_db)):
    mechanic = schemas.MechanicCreate(login=login,password=password,first_name=first_name, last_name=last_name, is_admin=is_admin)
    crud.create_mechanic(db=db,mechanic=mechanic)
    return responses.RedirectResponse("/create_mechanic", status_code=status.HTTP_302_FOUND)

@app.get("/mechanics/", response_model=list[schemas.Mechanic])
def read_mechanics(request: Request, db: Session = Depends(get_db)):
    mechanics = crud.get_mechanics(db)
    context = {"request": request, "mechanics": mechanics}
    return templates.TemplateResponse("mechanics.html", context)



@app.get("/create_mechanic/")
def create_mechanic_form(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("create_mechanic.html", context)


@app.delete("/delete_mechanic/{mechanic_id}")
def delete_mechanic(mechanic_id: int, db: Session = Depends(get_db)):
    return crud.delete_mechanic(db=db,mechanic_id=mechanic_id)


@app.post("/create_repair/")
def create_repair(repair: schemas.RepairCreate, db: Session = Depends(get_db)):
    return crud.create_repair(db=db,repair=repair)

@app.get("/repairs/", response_model=list[schemas.Repair])
def read_repairs(request: Request, db: Session = Depends(get_db)):
    repairs = crud.get_repairs(db)
    context = {"request": request, "repairs": repairs}
    return templates.TemplateResponse("repairs.html", context)


@app.get("/repairs/{repair_id}", response_model=schemas.Repair)
def read_repair(request: Request, repair_id: int, db: Session = Depends(get_db)):
    repair = crud.get_repair(db=db, repair_id=repair_id)
    context = {"request": request, "repair": repair}
    return context

