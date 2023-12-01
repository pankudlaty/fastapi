from fastapi import FastAPI, Request, Response, Depends,  Form, responses, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import True_
from sqlalchemy.orm import Session
from jose import jwt
from .database import SessionLocal, engine
from . import models, schemas, crud
from .utils import OAuth2PasswordBearerWithCookie
from .hasher import Hasher

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")
SECERET_KEY = "b801b7d7e6a3f3132ad8e3a8c3956c2270f6d1b3ae65c957583295db3711372c"
ALGORITHM = "HS256"

templates = Jinja2Templates(directory="sql_app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def get_user_from_token(db, token):
    try:
        payload = jwt.decode(token, SECERET_KEY, algorithms=[ALGORITHM])
        login = payload.get("sub")
        if not login:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate creds")
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate creds")
    user = db.query(models.Mechanic).filter(models.Mechanic.login == login).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate creds")
    return user

@app.post("/login/token")
def retrive_token_for_authenticated_user(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    mechanic = db.query(models.Mechanic).filter(models.Mechanic.login == form_data.username).first()
    if not mechanic:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong username")
    if not Hasher.verify_password(form_data.password, mechanic.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password")
    data = {"sub": form_data.username}
    jwt_token = jwt.encode(data, SECERET_KEY, algorithm=ALGORITHM)
    response.set_cookie(key="access_token", value=f"Bearer {jwt_token}",httponly=True)
    return {"access_token": jwt_token, "token_type": "bearer"}



@app.get("/")
def login_form(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("login.html", context)

@app.post("/")
def login(response: Response, request: Request, login: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    login = login
    password = password
    err = []
    context = {"request": request, "errors": err}
    try:
        mechanic = db.query(models.Mechanic).filter(models.Mechanic.login == login).first()
        if mechanic is None:
            err.append("Login does not exist")
            return templates.TemplateResponse("login.html", context)
        else:
            if Hasher.verify_password(password, mechanic.hashed_password):
                data = {"sub":login}
                jwt_token = jwt.encode(data,SECERET_KEY,algorithm=ALGORITHM)
                response = responses.RedirectResponse("/repairs",status_code=status.HTTP_302_FOUND)
                response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
                return response
            else:
                err.append("Wrong password")
                return templates.TemplateResponse("login.html", context)
    except:
        err.append("Problem with auth or storing token")
        return templates.TemplateResponse("login.html", context)

@app.post("/create_mechanic/")
def create_mechanic( login: str = Form(...),first_name: str = Form(...), last_name: str = Form(...),password: str = Form(...),is_admin: bool = Form(False),  db: Session = Depends(get_db)):
    mechanic = schemas.MechanicCreate(login=login,password=password,first_name=first_name, last_name=last_name, is_admin=is_admin)
    crud.create_mechanic(db=db,mechanic=mechanic)
    return responses.RedirectResponse("/create_mechanic", status_code=status.HTTP_302_FOUND)

@app.get("/mechanics/", response_model=list[schemas.Mechanic])
def read_mechanics(request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    mechanic = get_user_from_token(db, token)
    if not mechanic.is_admin:
        return templates.TemplateResponse("denied.html", {"request": request})
    mechanics = crud.get_mechanics(db)
    context = {"request": request, "mechanics": mechanics}
    return templates.TemplateResponse("mechanics.html", context)



@app.get("/create_mechanic/")
def create_mechanic_form(request: Request,db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    mechanic = get_user_from_token(db, token)
    context = {"request": request}
    if not mechanic.is_admin:
        return templates.TemplateResponse("denied.html", context)
    return templates.TemplateResponse("create_mechanic.html", context)


@app.delete("/delete_mechanic/{mechanic_id}")
def delete_mechanic(mechanic_id: int, db: Session = Depends(get_db)):
    crud.delete_mechanic(db=db,mechanic_id=mechanic_id)

@app.get("/create_repair/")
def create_repair_form(request: Request,db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    context = {"request": request}
    mechanic = get_user_from_token(db, token)
    if not mechanic.is_admin:
        return templates.TemplateResponse("denied.html", context)
    return templates.TemplateResponse("create_repair.html", context)

@app.post("/create_repair/")
def create_repair(manufacturer: str = Form(...), model: str = Form(...), kind: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    repair = schemas.RepairCreate(manufacturer=manufacturer, model=model, kind=kind, description=description)
    crud.create_repair(db=db,repair=repair)
    return responses.RedirectResponse("/create_repair", status_code=status.HTTP_302_FOUND)


@app.get("/repairs/", response_model=list[schemas.Repair])
def read_repairs(request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    mechanic = get_user_from_token(db, token)
    mechanic_is_admin = bool(mechanic.is_admin)
    mechanic_id = mechanic.id
    if not mechanic_is_admin:
        repairs = crud.get_repairs_for_mechanic(db=db,mechanic_id=mechanic_id)
        context = {"request": request, "repairs": repairs}
        return templates.TemplateResponse("repairs.html", context)
    repairs = crud.get_repairs(db)
    context = {"request": request, "repairs": repairs}
    return templates.TemplateResponse("repairs.html", context)

@app.patch("/repair/{repair_id}/mechanic/{mechanic_id}")
def assign_repair(repair_id: int, mechanic_id: int, db: Session = Depends(get_db)):
    return crud.assign_repair(db=db,mechanic_id=mechanic_id,repair_id=repair_id)

