from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.orm import Session
from translatorapi.schemas.userschemas import ApiKeyResponse
from translatorapi.services.userservice import get_current_user
from translatorapi.db import database
from translatorapi.mymodel import models
from translatorapi import dependencies
router=APIRouter(
    prefix="/apikey",
    tags=["APIKey"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/create", response_model=ApiKeyResponse)
def create_api_key(db: Session = Depends(database.get_db),current_user:models.Users=Depends(get_current_user)):
    existing_api_key =db.query(models.APIKey).filter(models.APIKey.owner_id == current_user.id).first()
    if existing_api_key:
        #replacing with the new one
        new_key=dependencies.generate_api_key()
        existing_api_key.key=new_key
        db.commit()
        db.refresh(existing_api_key)
        return ApiKeyResponse(key=existing_api_key.key)
    else:
        new_key=dependencies.generate_api_key()
        new_api_key=models.APIKey(owner_id=current_user.id,key=new_key)
        db.add(new_api_key)
        db.commit()
        db.refresh(new_api_key)
        return ApiKeyResponse(key=new_api_key.key)
    

@router.get("/getapikey",response_model=ApiKeyResponse)
def get_api_key(db:Session=Depends(database.get_db),current_user:models.Users=Depends(get_current_user)):
    api_key=db.query(models.APIKey).filter(models.APIKey.owner_id==current_user.id).first()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No API Key found for this user")
    return ApiKeyResponse(key=api_key.key)

@router.delete("/deleteapikey",response_model=ApiKeyResponse)
def delete_api_key(db:Session=Depends(database.get_db),current_user:models.Users=Depends(get_current_user)):
    api_key=db.query(models.APIKey).filter(models.APIKey.owner_id==current_user.id).first()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No API Key found for this user")
    db.delete(api_key)
    db.commit()
    return {"detail":"APi key deleted successfully"}