# app/web/routes.py

from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from translatorapi.schemas.userschemas import Createuserrequest,Token,ApiKeyResponse
from translatorapi.services.userservice import authenticate_user,create_access_token,get_current_user
from translatorapi.mymodel.models import Users,APIKey
from translatorapi.db.database import  get_db
from datetime import timedelta
from translatorapi.dependencies import get_translate_services
from jose import jwt, JWTError
import os
import logging

logger = logging.getLogger(__name__)
from translatorapi.services.userservice import get_password_hash
from translatorapi.dependencies import generate_api_key
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY =os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')


ACCESS_TOKEN_EXPIRE_MINUTES= int(os.getenv('ACCESS_TOKEN_EXPIRE'))


router=APIRouter(
    prefix="",
    tags=['web']
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
# print(BASE_DIR)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))




def set_access_token_cookie(response:RedirectResponse,access_token:str):
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True,path="/")

    return response

def get_current_user_from_cookie(request:Request,db:Session=Depends(get_db))-> Users:
    token=request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        token=token.replace("Bearer","")
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get("sub")
        user_id:int=payload.get("user_id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user=db.query(Users).filter(Users.username==username,Users.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user




@router.get("/signup",response_class=HTMLResponse)
def signup(request:Request):
    return templates.TemplateResponse("signup.html",{"request":request})



@router.post("/signup",response_class=HTMLResponse)
def signup(request:Request,username:str=Form(...),password:str=Form(...),db:Session=Depends(get_db)):
    existing_user=db.query(Users).filter(Users.username==username).first()
    if existing_user:
        return templates.TemplateResponse("signup.html", {"request": request, "message": "Username already exists."})
    hashed_password = get_password_hash(password)
    new_user = Users(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    accesstoken=create_access_token(new_user.username,new_user.id,timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response=RedirectResponse(url="/",status_code=status.HTTP_302_FOUND)
    set_access_token_cookie(response,accesstoken)
    return response



@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    logger.info(f"Authenticating user: {username}")
    user = authenticate_user(username, password, db)
    
    if not user:
        logger.warning("Authentication failed.")
        return templates.TemplateResponse("login.html", {"request": request, "message": "Invalid credentials."})
    logger.info("Authentication successful.")
    access_token = create_access_token(user.username, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    set_access_token_cookie(response, access_token)
    return response

@router.get("/logout", response_class=HTMLResponse)
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        user = get_current_user_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    api_key = db.query(APIKey).filter(APIKey.owner_id == user.id).first()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": user.username,
        "api_key_exists": bool(api_key),
    })

@router.post("/apikey/create", response_class=HTMLResponse)
def create_api_key_web(request: Request, db: Session = Depends(get_db)):
    try:
        user = get_current_user_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    existing_api_key = db.query(APIKey).filter(APIKey.owner_id == user.id).first()
    new_key = generate_api_key()

    if existing_api_key:
        # Replace existing API key
        existing_api_key.key =new_key
        db.commit()
        db.refresh(existing_api_key)
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "username": user.username,
            "api_key_exists": True,
            "api_key": new_key,
            "message": "API Key regenerated successfully."
        })
    else:
        # Create new API key
        api_key = APIKey(owner_id=user.id, key=new_key)
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "username": user.username,
            "api_key_exists": True,
            "api_key": new_key,
            "message": "API Key created successfully."
        })

@router.post("/apikey/deleteapikey", response_class=HTMLResponse)
def delete_api_key_web(request: Request, db: Session = Depends(get_db)):
    try:
        user = get_current_user_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    api_key = db.query(APIKey).filter(APIKey.owner_id == user.id).first()
    if not api_key:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "username": user.username,
            "api_key_exists": False,
            "message": "No API Key found to delete."
        })
    db.delete(api_key)
    db.commit()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": user.username,
        "api_key_exists": False,
        "message": "API Key deleted successfully."
    })

@router.post("/translate", response_class=HTMLResponse)
async def translate_dashboard(request: Request, sentence: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    
    # Perform the translation
    service = get_translate_services()
    translated_sentence = service.translate(sentence)
    
    # Retrieve API key for the user
    api_key = db.query(APIKey).filter(APIKey.owner_id == user.id).first()
    
    # Re-render the dashboard with the translated sentence
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": user.username,
        "translated_sentence": translated_sentence,
        "api_key_exists": bool(api_key),
        "api_key": api_key.key if api_key else None
    })