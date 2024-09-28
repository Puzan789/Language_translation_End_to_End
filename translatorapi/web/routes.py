# app/web/routes.py

from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..schemas import UserCreate, Token, APIKeyResponse
from ..auth import authenticate_user, create_access_token, get_current_user, get_db
from ..mymodel import User, APIKey
from ..utils import get_password_hash, generate_api_key, hash_api_key
from datetime import timedelta
from jose import jwt, JWTError
import os

router = APIRouter(
    prefix="",  # No prefix for web routes
    tags=["Web"],
)

templates = Jinja2Templates(directory="app/web/templates")

# Load environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def set_access_token_cookie(response: RedirectResponse, token: str):
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.username == username, User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup", response_class=HTMLResponse)
def signup(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("signup.html", {"request": request, "message": "Username already exists."})
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Automatically log in the user after signup
    access_token = create_access_token(new_user.username, new_user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    set_access_token_cookie(response, access_token)
    return response

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(username, password, db)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "message": "Invalid credentials."})
    access_token = create_access_token(user.username, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    set_access_token_cookie(response, access_token)
    return response

@router.get("/logout", response_class=HTMLResponse)
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
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
    hashed_new_key = hash_api_key(new_key)

    if existing_api_key:
        # Replace existing API key
        existing_api_key.key = hashed_new_key
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
        api_key = APIKey(owner_id=user.id, key=hashed_new_key)
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
