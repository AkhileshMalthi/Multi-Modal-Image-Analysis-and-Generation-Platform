from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use PostgreSQL if configured, otherwise fallback to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to SQLite for development
    DATABASE_URL = "sqlite:///./app.db"
    print(f"⚠️  Using SQLite database (development mode): {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
elif "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
    # Use PostgreSQL in production
    print(f"✅ Using PostgreSQL database")
    engine = create_engine(DATABASE_URL)
else:
    # Other database types (MySQL, etc.)
    print(f"✅ Using configured database")
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()