from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine("sqlite:///example.db")  # Adjust with your DB connection string
Base = declarative_base()
