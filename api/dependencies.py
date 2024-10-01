from translator.pipeline.stage_05_datatranslate import TranslateService
import secrets
from fastapi import Request



def get_translate_service(request: Request) -> TranslateService:
    return request.app.state.translate_service
