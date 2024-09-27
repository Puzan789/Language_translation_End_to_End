from translator.pipeline.stage_05_datatranslate import TranslateService

translate_services=None

def get_translate_services():
    global translate_services
    if translate_services is None:
        translate_services=TranslateService()
    return translate_services