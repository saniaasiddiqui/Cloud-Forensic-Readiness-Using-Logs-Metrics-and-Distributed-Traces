from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# SQLite database file banayenge
SQLALCHEMY_DATABASE_URL = "sqlite:///./forensic.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Incident Table
class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, index=True)
    trace_id = Column(String, index=True)
    service_name = Column(String)
    severity = Column(String)
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database tables create karein
Base.metadata.create_all(bind=engine)
