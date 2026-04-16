import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import exc
from passlib.context import CryptContext

from . import models, schemas
from .database import engine, get_db

# En un entorno de producción, cargar desde variables de entorno
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Para SQLite u otros entornos que no tengan la estructura del schema importado manualmente,
# sqlalchemy intentará crear las tablas. Para MySQL mejor usar el database_schema.sql y quitar esto.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GLPI Ayto Aranjuez")

# ================================
# API ROUTES
# ================================

@app.post("/api/login", response_model=schemas.Token)
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Fake login temporal hasta disponer de JWT y contraseñas hasheadas en base de datos.
    # Como la BD deviene vacía de usuarios, permitiremos autoacceso.
    user = db.query(models.User).filter(models.User.username == req.username).first()
    
    if not user:
        # Dummy system: si no existe y usamos 'admin', lo creamos bajo el rol 1 (Admin)
        if req.username == 'admin' or 'tecnico' in req.username or 'user' in req.username:
            role_id = 1 if req.username == 'admin' else (2 if 'tecnico' in req.username else 3)
            user = models.User(username=req.username, password_hash=pwd_context.hash(req.password), email=f"{req.username}@aranjuez.es", role_id=role_id)
            db.add(user)
            try:
                db.commit()
                db.refresh(user)
            except exc.IntegrityError:
                db.rollback()

    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    return {"access_token": user.username, "token_type": "bearer"} # Aquí usamos usename temporalmente

@app.get("/api/users/me", response_model=schemas.User)
def read_users_me(access_token: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == access_token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.get("/api/categories", response_model=list[schemas.Category])
def read_categories(all: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.Category)
    if not all:
        query = query.filter(models.Category.is_visible_to_users == True)
    return query.all()

@app.get("/api/tickets", response_model=list[schemas.Ticket])
def read_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).all()

@app.post("/api/tickets", response_model=schemas.Ticket)
def create_ticket(ticket: schemas.TicketCreate, access_token: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == access_token).first()
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")

    db_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        category_id=ticket.category_id,
        priority=ticket.priority,
        requester_id=user.id
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

# ================================
# SERVE FRONTEND (SPA)
# ================================
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
os.makedirs(os.path.join(frontend_path, "static", "css"), exist_ok=True)
os.makedirs(os.path.join(frontend_path, "static", "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    return FileResponse(os.path.join(frontend_path, "index.html"))
