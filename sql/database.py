from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import URL


connection_url = URL.create(
    "mssql+pyodbc",
    username="sa",
    password="12345678",
    host="localhost",
    database="deepmuscle-dev",
    query={"driver": "ODBC Driver 17 for SQL Server"},
)

engine = create_engine(
    connection_url
)

conn = engine.connect()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()