from fastapi import FastAPI,Depends
from contextlib import asynccontextmanager
from translatorapi.dependencies import get_translate_services
from translatorapi.db.database import Base,engine
import logging
import sys
print("pathis",sys.path)
from translatorapi.services import userservice
from translatorapi.routes import user,apikey
logger = logging.getLogger('watchfiles.main')
logger.setLevel(logging.WARNING)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("model_loaded")
    get_translate_services()
    yield 
    print("model_unloaded")


app=FastAPI(lifespan=lifespan)
app.include_router(user.router)
app.include_router(apikey.router)

@app.get("/translate")
async def translate(sentence:str,current_user: dict = Depends(userservice.get_current_user)):
    service=get_translate_services()
    translated_sentence=service.translate(sentence)
    return {"translated_sentence": translated_sentence,"user": current_user}


