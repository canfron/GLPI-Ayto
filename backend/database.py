from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuraremos la conexión para que apunte al servidor phpMyAdmin local
# Cambiar las credenciales de root por las reales si fuera necesario.
# Por defecto asumimos que phpMyAdmin tiene un usuario root u otro creado para el GLPI.
# Para desarrollo usaremos sqlite local si no detectamos la base de datos MySQL

import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./glpi_ayto.db") 

# Descomentar y ajustar ruta MySQL cuando el servicio este operando
# DATABASE_URL = "mysql+pymysql://root:password@90.0.50.100:3306/glpi_ayto"

kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
