from fastapi import APIRouter,Request,Depends,status,HTTPException,Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from api.models.models import User,APIKey
from api.db.database import get_db
import os
from api.routes.auth_web import set_access_token_cookie,TEMPLATES_DIR,templates
from api.services.auth_service import get_current_user
from api.dependencies import get_translate_service
from translator.pipeline.stage_05_datatranslate import TranslateService
from api.dependencies import get_translate_service




router=APIRouter(
    prefix="",
    tags=["Web"]
)

@router.get("/dashboard",response_class=HTMLResponse)
def dashboard(request:Request,db:Session=Depends(get_db)):
    try:
        current_user = get_current_user(request, db)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    api_key=db.query(APIKey).filter(APIKey.owner_id==current_user.id).first()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": current_user.username,
        "api_key_exists": bool(api_key),
        "api_key": api_key.key if api_key else None
    })

@router.post("/translate",response_class=HTMLResponse)
def translate_sentence_web(
    request:Request,
    sentence:str=Form(...),
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user),
    translator:TranslateService=Depends(get_translate_service),
):

    translated_sentence=translator.translate(sentence)
    api_key = db.query(APIKey).filter(APIKey.owner_id == current_user.id).first()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": current_user.username,
        "api_key_exists": bool(api_key),
        "api_key": api_key.key if api_key else None,
        "translated_sentence": translated_sentence
    })

@router.post("/logout", response_class=RedirectResponse)
def logout_web(request: Request):
    response=RedirectResponse(url="/login",status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token", path="/")
    return response

              

