import os
from typing import Generator
from dotenv import load_dotenv
from sqlmodel import Session, create_engine
from sqlalchemy.pool import StaticPool

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./incident_platform.db")

# Handle SQLite vs PostgreSQL configuration
connect_args = {}
poolclass = None

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # If in-memory or file-based sqlite for tests/local
    if ":memory:" in DATABASE_URL:
        poolclass = StaticPool

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    poolclass=poolclass if poolclass else None,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session