from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import get_settings

class Base(DeclarativeBase):
    pass

def _database_url() -> str:
    configured = get_settings().database_url.strip()
    if configured:
        return configured
    return f"sqlite:///{(get_settings().backend_dir / 'agrivision.db').as_posix()}"

def _make_engine():
    url = _database_url()
    options = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=options, pool_pre_ping=True)

engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
