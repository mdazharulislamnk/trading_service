from sqlmodel import SQLModel, create_engine
import os

# Use SQLite for simplicity initially, but easy to switch to Postgres
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading.db")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
