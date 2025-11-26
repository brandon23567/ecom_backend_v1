from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os 

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Unable to get the database url and load it")


Base = declarative_base()

engine = create_engine(DATABASE_URL, echo=True)

LocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

def get_db():
    db = LocalSession()
    try:
        yield db 
    finally:
        db.close()
        
        