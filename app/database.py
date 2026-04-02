from sqlmodel import SQLModel, create_engine
import os

# Use SQLite for simplicity initially, but easy to switch to Postgres
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading.db")

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
