from sqlalchemy import Column, Integer, Float, DateTime, String
from datetime import datetime

from backend.database.database import Base


class AnalyticsRecord(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)

    people = Column(Integer)
    cars = Column(Integer)
    buses = Column(Integer)
    motorcycles = Column(Integer)

    fps = Column(Float)

    line_crossings = Column(Integer)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    from sqlalchemy import String

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True)

    email = Column(String, unique=True, index=True)

    password = Column(String)