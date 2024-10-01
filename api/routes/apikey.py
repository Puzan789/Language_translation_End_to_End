from fastapi import APIRouter,Depends,HTTPException,status
from api.schemas.userschemas import ApiKeyResponse
from api.db.database import get_db
from sqlalchemy.orm import Session
from api.models.models import User,APIKey
from api.services.auth_service import get_current_user,generate_api_key


router=APIRouter(
    prefix="/api",
    tags=["API Key Management"]
)

@router.post("/apikey/create",response_model=ApiKeyResponse)
def create_api_key(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    existing_api_key=db.query(APIKey).filter(APIKey.owner_id==current_user.id).first()
    new_key=generate_api_key()
    if existing_api_key:
        existing_api_key.key=new_key
        db.commit()
        db.refresh(existing_api_key)
        return ApiKeyResponse(key=existing_api_key.key)
    else:
        new_api_key=APIKey(owner_id=current_user.id,key=new_key)
        db.add(new_api_key)
        db.commit()
        db.refresh(new_api_key)
        return ApiKeyResponse(key=new_api_key.key)

@router.get("/apikey",response_model=ApiKeyResponse)
def get_api_key(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    api_key=db.query(APIKey).filter(APIKey.owner_id==current_user.id).first()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found.")
    return ApiKeyResponse(key=api_key.key)

@router.post("/apikey/delete")  
def delete_api_key(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    api_key = db.query(APIKey).filter(APIKey.owner_id == current_user.id).first()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found.")
    
    db.delete(api_key)
    db.commit()
    return {"detail": "API key deleted successfully"}

