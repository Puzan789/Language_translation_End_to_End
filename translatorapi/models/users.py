from translatorapi.db.database import Base
from sqlalchemy import Column,ForeignKey,Boolean,String,Integer,DateTime
from datetime import datetime
from sqlalchemy.sql import func

class Users(Base):
    __tablename__ = 'users'
    
    id=Column(Integer, primary_key=True,index=True)
    username=Column(String, unique=True, index=True)
    # email=Column(String, unique=True, index=True)
    hashed_password=Column(String)
    # is_active=Column(Boolean,default=False)
    # created_at = Column(DateTime, default=func.now()) 

  
    
