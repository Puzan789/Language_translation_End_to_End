
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from translatorapi.mymodel.models import Users
from datetime import datetime, timedelta,timezone
from fastapi import HTTPException,Depends,status
from sqlalchemy.orm import Session
import jwt
import logging

logger = logging.getLogger(__name__)
from jose import JWTError
from translatorapi.db.database import get_db
import os
from dotenv import load_dotenv
load_dotenv()



bcryptcontext = CryptContext(schemes=['bcrypt'], deprecated='auto') #hasshing algorithm
oauth_bearer=OAuth2PasswordBearer(tokenUrl='/auth/token')

SECRET_KEY =os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')


ACCESS_TOKEN_EXPIRE_MINUTES= int(os.getenv('ACCESS_TOKEN_EXPIRE'))

def get_password_hash(password:str)->str:
    return bcryptcontext.hash(password)


def authenticate_user(username:str,password:str,db):
    user=db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcryptcontext.verify(password,user.hashed_password):
        return False
    return user



def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    # Create the JWT payload
    encode = {"sub": username, 'user_id': user_id}
    
    # Set expiration time
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires.timestamp()})
    
    # Encode the JWT
    access_token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Log the generated token
    logger.info(f"Access token: {access_token}")
    
    return access_token


    
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
