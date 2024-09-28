
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from passlib.context import CryptContext
from translatorapi.mymodel.models import Users
from datetime import datetime, timedelta,timezone
from fastapi import HTTPException,Depends,status
from sqlalchemy.orm import Session
import jwt
from typing import Annotated
from jose import JWTError
import secrets 
from translatorapi.db.database import get_db

SECRET_KEY = 'Hello world!'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE=30

bcryptcontext = CryptContext(schemes=['bcrypt'], deprecated='auto') #hasshing algorithm
oauth_bearer=OAuth2PasswordBearer(tokenUrl='/auth/token')

def authenticate_user(username:str,password:str,db):
    user=db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcryptcontext.verify(password,user.hashed_password):
        return False
    return user

def create_access_token(username:str,user_id:int,expires_delta:timedelta):
    encode={"sub":username,'id':user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"expires":expires.timestamp()})
    return jwt.encode(encode,SECRET_KEY,ALGORITHM)

async def get_current_user(token:Annotated[str,Depends(oauth_bearer)]):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get('sub')
        user_id:int=payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validateuser")
        return {"username":username, "user_id":user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate user")


    
def get_current_user(token: str = Depends(oauth_bearer), db: Session = Depends(get_db)) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(Users).filter(Users.username == username, Users.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
