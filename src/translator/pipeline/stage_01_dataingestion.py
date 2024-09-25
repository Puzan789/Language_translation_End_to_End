#pipeline
from translator.components.dataingestion import Dataingestion
from translator.entity import DataIngestionConfig
from translator.config.configuration import ConfigurationManager
from translator.logging import logger

class DataIngestionTrainingPipeline:
    def __init__(self):
        pass
    def main(self):
        try:
            config=ConfigurationManager()
            data_ingestion_config=config.get_data_ingestion_config()
            dataingestion=Dataingestion(data_ingestion_config)
            dataingestion.download_file()
            dataingestion.extract_zip_file()
        except Exception as e:
            logger.error(f"An error occured while")
            raise e
    