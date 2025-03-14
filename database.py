from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

server = "ESTEBANBARRERA\SQLEXPRESS"
dbname = "ACERONET"  

DATABASE_URL = f"mssql+pyodbc://{server}/{dbname}?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
