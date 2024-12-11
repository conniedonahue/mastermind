from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()
"""
SQLAlchemy declarative base class for ORM models.
All database models should inherit from this class.
"""