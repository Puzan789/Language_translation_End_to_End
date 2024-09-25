from translator.components.datavalidation import Datavalidation
from translator.config.configuration import ConfigurationManager



class DataValidationTrainingPipeline:
    def __init__(self) -> None:
        pass
        
    def main(self):
        try:
            config=ConfigurationManager()
            data_validation_config=config.get_data_validation_config()
            data_validation=Datavalidation(config=data_validation_config)
            data_validation.validate_all_files_exist()
        except Exception as e:
            raise e


