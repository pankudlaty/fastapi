from typing import Optional
from fastapi import FastAPI, Request, Header, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


templates = Jinja2Templates(directory="sql_app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/index/', response_class=HTMLResponse)
def movielist(
    request: Request,
    hx_request: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
   films = [
            {'name': 'Blade Runner', 'director': 'Ridley Scott'},
            {'name': 'Pulp Fiction', 'director': 'Quentin Tarantino'},
            {'name': 'Mulholland Drive', 'director': 'David Lynch'},
    ]
   context = {'request': request, 'films': films}
   if hx_request:
       return templates.TemplateResponse("table.html", context)
   return templates.TemplateResponse("index.html", context)

