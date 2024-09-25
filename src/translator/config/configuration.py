import os
from pathlib import Path
from translator.entity import DataIngestionConfig
from translator.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH
from translator.utils.common import read_yaml,create_directories,get_size
from translator.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH
from translator.utils.common import read_yaml,create_directories,get_size


class ConfigurationManager:
    def __init__(self,config_file_path=CONFIG_FILE_PATH,params_file_path=PARAMS_FILE_PATH):
        self.config=read_yaml(config_file_path)
        self.params=read_yaml(params_file_path)
        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion
        create_directories([Path(config.root_dir)])  # Ensure it's a Path object
        data_ingestion_config = DataIngestionConfig(
            root_dir=Path(config.root_dir),  # Convert to Path object
            source_URL=config.source_URL,
            local_data_file=Path(config.local_data_file),  # Convert to Path object
            unzip_dir=Path(config.unzip_dir),  # Convert to Path object
        )
        return data_ingestion_config