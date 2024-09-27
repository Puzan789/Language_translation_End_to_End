from translator.config.configuration import ConfigurationManager
from translator.components.modeltranslate import Load_model

class TranslateService:
    def __init__(self):
        try:
            
            config = ConfigurationManager()
            data_translate_config = config.get_model_translate_config()
            self.mod = Load_model(data_translate_config)  # Create the model loader instance
            self.mod.load_model()  # Load the model and tokenizers (happens once)
        except Exception as e:
            raise e
        
    def translate(self, sentence):
        try:
            
            translated_sentence = self.mod.translate_sentence(sentence)
            return translated_sentence
        except Exception as e:
            raise e