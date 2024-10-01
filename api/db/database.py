from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL="sqlite:///./sql_app.db"

engine=create_engine(SQLALCHEMY_DATABASE_URL,
                     connect_args={"check_same_thread": False}
                     )

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()


#sessionlocal creates a new Session for each user request 
# engine: Handles the actual database connection.
# SessionLocal: Creates new Session objects (the workspace where you interact with the database).
# Session: A specific instance created by SessionLocal that you use to run queries, insert data, and commit/rollback transactions.
# Base: A base class that all your database models inherit from, representing tables in the database.
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()