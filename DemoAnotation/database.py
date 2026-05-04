"""
Configuração do banco de dados — SQLAlchemy + SQLite (dev) / PostgreSQL (prod)

Author: Christopher N. S. M. Mauricio
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENVIRONMENT", "dev")

if ENV == "prod":
    host     = os.getenv("POSTGRES_HOST", "localhost")
    port     = os.getenv("POSTGRES_PORT", "5432")
    user     = os.getenv("POSTGRES_USER", "odata_user")
    password = os.getenv("POSTGRES_PASSWORD", "")
    dbname   = os.getenv("POSTGRES_DB", "odata_demo")
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
else:
    sqlite_path  = os.getenv("SQLITE_DB", "./demo.db")
    db_dir       = os.path.dirname(sqlite_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    DATABASE_URL = f"sqlite:///{sqlite_path}"

print(f"[DB] Conectando: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Única instância de Base usada por todos os modelos
Base = declarative_base()


def get_db():
    """Dependency do FastAPI — abre e fecha a sessão por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
