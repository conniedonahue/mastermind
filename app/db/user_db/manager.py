from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, scoped_session
from flask import current_app
import os
from .base import Base
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig


environment = os.getenv("FLASK_ENV", "development")

if environment == "production":
    config = ProductionConfig
elif environment == "testing":
    config = TestingConfig
else:
    config = DevelopmentConfig

Session = scoped_session(sessionmaker())

def init_db(app):
    global engine, Session
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    Session.configure(bind=engine)
    app.teardown_appcontext(close_session)
    return engine

def close_session(exception=None):
    Session.remove()
