from fastapi import FastAPI,Depends
from contextlib import asynccontextmanager
from api.routes import auth_api,apikey,auth_web,web
from api.db.database import Base,engine

from translator.pipeline.stage_05_datatranslate import TranslateService

from fastapi.staticfiles import StaticFiles
import logging
import sys
logger = logging.getLogger('watchfiles.main')
logger.setLevel(logging.WARNING)
Base.metadata.create_all(bind=engine)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize TranslateService once at startup
    logger.info("Initializing TranslateService...")
    app.state.translate_service = TranslateService()
    yield
    # Clean up if necessary on shutdown
    logger.info("Shutting down TranslateService...")
    del app.state.translate_service

# Initialize FastAPI with the lifespan context manager
app = FastAPI(lifespan=lifespan)
app.include_router(auth_api.router)
app.include_router(apikey.router)
app.include_router(auth_web.router)
app.include_router(web.router)


app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.mount("/static", StaticFiles(directory="web/static"), name="static")