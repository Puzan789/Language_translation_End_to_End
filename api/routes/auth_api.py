from fastapi import APIRouter,Depends,status,HTTPException
from api.db.database import get_db
from sqlalchemy.orm import Session
from typing import Annotated
from api.schemas.userschemas import Createuserrequest,Token,TranslateResponse,TranslateRequest
from api.models.models import User
from api.services.auth_service import get_password_hash,authenticate_user,ACCESS_TOKEN_EXPIRE_MINUTES,get_current_user_api_key,create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from api.dependencies import get_translate_service
from translator.pipeline.stage_05_datatranslate import TranslateService

router=APIRouter(
    prefix='/auth',
    tags=['API Authentication']
)
db_dependency=Annotated[Session,Depends(get_db)]

@router.post("/signup",status_code=status.HTTP_201_CREATED)
def api_signup(user_request:Createuserrequest,db:Session=Depends(get_db)) :
    existing_user=db.query(User).filter(User.username==user_request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    hashed_password=get_password_hash(user_request.password)
    new_user=User(username=user_request.username,hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message":"User created successfully"}

@router.post("/token",response_model=Token)
def api_login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:Session=Depends(get_db)):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    access_token_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token=create_access_token(user.username,user.id,expires_delta=access_token_expires)
    return {"access_token":access_token,"token_type":"bearer"}


@router.post("/translate", response_model=TranslateResponse, tags=["Apitranslate"])
def translate_text_api(
    request: TranslateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_api_key),
    translator: TranslateService = Depends(get_translate_service)  
):
    try:
        translated_text = translator.translate(request.text)
        return TranslateResponse(translated_text=translated_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )
    