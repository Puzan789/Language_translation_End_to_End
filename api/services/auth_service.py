from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer,APIKeyHeader

from api.models.models import User,APIKey
from api.db.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime,timedelta
from jose import JWTError,jwt
from fastapi import HTTPException,status,Depends,Request,HTTPException,Security
from functools import lru_cache
import os 
from api.models.models import User
from dotenv import load_dotenv
import secrets
import logging
import secrets


load_dotenv()

logger=logging.getLogger(__name__)

pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth_bearer=OAuth2PasswordBearer(tokenUrl='/auth/token')

#configuration
SECRET_KEY=os.getenv('SECRET_KEY')
ALGORITHM=os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv('ACCESS_TOKEN_EXPIRE'))
API_KEY_NAME = "T-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_password_hash(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username:str,password:str,db:Session)-> User:
    user=db.query(User).filter(User.username==username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not verify_password(password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    return user
# def get_current_user(token: str = Depends(oauth_bearer), db: Session = Depends(get_db)) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials.",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         user_id: int = payload.get("user_id")
#         if username is None or user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#     user = db.query(User).filter(User.username == username, User.id == user_id).first()
#     if user is None:
#         raise credentials_exception
#     return user
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    logger.debug("Attempting to retrieve token from headers or cookies.")

    # Try to get token from Authorization header
    token = None
    authorization: str = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer "):]
        logger.debug("Token retrieved from Authorization header.")
    else:
        # Try to get token from cookie
        token = request.cookies.get("access_token")
        if token and token.startswith("Bearer "):
            token = token[len("Bearer "):]
            logger.debug("Token retrieved from access_token cookie.")

    if not token:
        logger.warning("No token found in Authorization header or access_token cookie.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            logger.error("Token payload missing 'sub' or 'user_id'.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        logger.error(f"JWT decoding failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username, User.id == user_id).first()
    if user is None:
        logger.error("User not found for the given token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"User authenticated: {user.username}")
    return user


def create_access_token(username:str,user_id:int,expires_delta:timedelta=None)->str:
    "creates a jwt access token"
    to_encode=dict(sub=username,user_id=user_id)
    if expires_delta:
        expire=datetime.now()+expires_delta
    else:
        expire=datetime.now()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_api_key()->str:
    return secrets.token_hex(32)



#for api key
def get_current_user_api_key(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    if not api_key:
        logger.warning("API Key missing in request headers.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing",
            headers={"WWW-Authenticate": "API Key"},
        )
    
    # Lookup the API key in the database
    api_key_obj = db.query(APIKey).filter(APIKey.key == api_key).first()
    if not api_key_obj:
        logger.warning("Invalid API Key provided.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "API Key"},
        )
    
    # Retrieve the associated user
    user = db.query(User).filter(User.id == api_key_obj.owner_id).first()
    if not user:
        logger.error("User associated with the provided API Key not found.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key: User not found",
            headers={"WWW-Authenticate": "API Key"},
        )
    
    logger.info(f"User authenticated via API Key: {user.username}")
    return user
