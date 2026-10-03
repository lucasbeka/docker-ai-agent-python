import os

import sqlmodel
from sqlmodel import Session, SQLModel

DATABSE_URL = os.environ.get("DATABSE_URL")

if DATABSE_URL == "":
    raise NotImplementedError("'DATABSE_URL' needs to be set.")

engine = sqlmodel.create_engine(DATABSE_URL)

def init_db():
    print("creating databeses tables...")
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session