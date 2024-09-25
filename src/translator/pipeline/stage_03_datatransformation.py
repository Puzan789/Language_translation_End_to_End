from translator.components.datatransform import DataTransformation,GetDataset
from translator.config.configuration import ConfigurationManager


class DataTransformationPipeline:
    def __init__(self) -> None:
        pass
    def main(self):
        try:
            config=ConfigurationManager()
            data_transformation_config=config.get_data_transformation_config()
            get_dataset=GetDataset(data_transformation_config)
            return get_dataset.get_ds()
        except Exception as e :
            raise e
        