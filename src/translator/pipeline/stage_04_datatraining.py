import torch
torch.cuda.empty_cache()
from translator.config.configuration import ConfigurationManager
from translator.components.modeltrain import Train_model

class ModelTrainingPipeline:
    def __init__(self):
        pass
    def main(self):
        try:
            config=ConfigurationManager()
            data_training_config=config.get_model_training_config()
            model_trainer=Train_model(config=data_training_config)
            model_trainer.trainmodel()
        except Exception as e :
            raise e
        
