from fastapi import APIRouter,Request,Depends,HTTPException,Form,status
from fastapi.responses import RedirectResponse,HTMLResponse
from sqlalchemy.orm import Session
import os
import jwt
from jose import JWTError
from fastapi.templating import Jinja2Templates
from api.db.database import get_db
from api.models.models import User
from api.services.auth_service import SECRET_KEY,ALGORITHM,get_password_hash,create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES,authenticate_user
from datetime import timedelta
from typing import Optional




router=APIRouter(
    prefix="",
    tags=["Web Authentication"]
)

#Template Directories
TEMPLATES_DIR=os.path.join(os.path.dirname(__file__), "../web/templates/")
templates=Jinja2Templates(directory=TEMPLATES_DIR)

def set_access_token_cookie(response: RedirectResponse, access_token: str) -> RedirectResponse:
    print(f"Setting access_token: {access_token}")
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,     
        samesite="strict", 
        path="/"
    )
    return response

def get_current_user_from_cookie(request:Request,db:Session=Depends(get_db))->User:
    token=request.cookies.get("access_token")
    print(f"Retrieved token: {token}")
    if not token:
        return None
    try:
        token=token.replace("Bearer ","")
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get("sub")
        user_id:int=payload.get("user_id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user=db.query(User).filter(User.username==username,User.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/signup",response_class=HTMLResponse)
def signup(request:Request,current_user:Optional[User]=Depends(get_current_user_from_cookie)):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    else:
        return templates.TemplateResponse("signup.html",{"request":request})

@router.post("/signup",response_class=HTMLResponse)
def signup(
    request:Request,
    username:str=Form(...),
    password:str=Form(...),
    db:Session=Depends(get_db)
):
    existing_user=db.query(User).filter(User.username==username).first()
    if existing_user:
        return templates.TemplateResponse("signup.html", {"request": request, "message": "Username already exists."})
    hashed_password=get_password_hash(password)
    new_user=User(username=username,hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token=create_access_token(new_user.username,new_user.id,timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response=RedirectResponse(url="/dashboard",status_code=status.HTTP_302_FOUND)
    set_access_token_cookie(response,access_token=access_token)
    return response

@router.get("/login",response_class=HTMLResponse)
def login(
    request:Request,
    current_user:Optional[User]=Depends(get_current_user_from_cookie)

):
    """Renders the webpage"""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    else:   
        return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login",response_class=HTMLResponse)
def login(
    request:Request,
    username:str=Form(...),
    password:str=Form(...),
    db:Session=Depends(get_db)
):
    """handling user login"""
    try:
        user=authenticate_user(username,password,db)
    except HTTPException:
        return templates.TemplateResponse("login.html", {"request": request, "message": "Invalid Username or Password."})
    access_token=create_access_token(user.username,user.id,timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response=RedirectResponse(url="/dashboard",status_code=status.HTTP_302_FOUND)
    set_access_token_cookie(response,access_token=access_token)
    return response


    