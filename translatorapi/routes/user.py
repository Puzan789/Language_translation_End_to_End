from fastapi import APIRouter,status,Depends,HTTPException
from translatorapi.models.users import Users
from translatorapi.schemas.userschemas import Createuserrequest,Token
from translatorapi.db.database import SessionLocal
from typing import Annotated
from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm
from translatorapi.services.userservice import authenticate_user,create_access_token,bcryptcontext

router=APIRouter(
    prefix='/auth',
    tags=['auth']
)


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency=Annotated[Session,Depends(get_db)]

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,create_userrequest:Createuserrequest):
    create_user_model=Users(
        username=create_userrequest.username,
        hashed_password=bcryptcontext.hash(create_userrequest.password)
    )
    try:
        db.add(create_user_model)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already exists"
        )



@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="couldnot validate user")
    token=create_access_token(user.username,user.id,timedelta(minutes=20))#jwt
    return {"access_token":token,"token_type":"bearer"}

