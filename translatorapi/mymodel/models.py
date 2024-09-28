from translatorapi.db.database import Base
from sqlalchemy import Column,ForeignKey,Boolean,String,Integer,DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Users(Base):
    __tablename__ = 'users'
    
    id=Column(Integer, primary_key=True,index=True)
    username=Column(String, unique=True, index=True)
    # email=Column(String, unique=True, index=True)
    hashed_password=Column(String)
    api_keys=relationship("APIKey",back_populates="owner")


class APIKey(Base):
    __tablename__ = 'api_keys'
    id=Column(Integer, primary_key=True,index=True)
    key=Column(String, unique=True, index=True)
    owner_id=Column(Integer, ForeignKey("users.id"))
    owner=relationship("Users",back_populates="api_keys")



