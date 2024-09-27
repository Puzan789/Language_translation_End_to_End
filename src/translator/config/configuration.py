import os
from pathlib import Path
from translator.entity import DataIngestionConfig,DataValidationConfig,DataTransformConfig,ModelTrainingConfig,ModelTranslateConfig
from translator.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH
from translator.utils.common import read_yaml,create_directories,get_size
from translator.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH
from translator.utils.common import read_yaml,create_directories,get_size


class ConfigurationManager:
    def __init__(self,config_file_path=CONFIG_FILE_PATH,params_file_path=PARAMS_FILE_PATH):
        print(os.getcwd())
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
    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation
        create_directories([Path(config.root_dir)])  # Ensure it's a Path object
        data_validation_config = DataValidationConfig(
            root_dir=Path(config.root_dir),  # Convert to Path object
            STATUS_FILE=config.STATUS_FILE,
            ALL_REQUIRED_FILES=config.ALL_REQUIRED_FILES
        )
        return data_validation_config
    def get_data_transformation_config(self)-> DataTransformConfig:
        config=self.config.data_transformation
        params=self.params.modeltrainer
        print(len(params))
        print("running")
        create_directories([config.root_dir])
        data_transformation_config=DataTransformConfig(
            root_dir=config.root_dir,
            data_path=config.data_path,
            tokenizer_file=config.tokenizer_file,
            max_seq_len=params.max_seq_len,
            src_lang=params.src_lang,
            tgt_lang=params.tgt_lang,
            src_file=config.src_file,
            tgt_file=config.tgt_file,
            batch_size=params.batch_size
        )
        return data_transformation_config
    def get_model_training_config(self)-> ModelTrainingConfig:
        config=self.config.data_training
        params=self.params.modeltrainer
        print(len(params))
        print("running")
        create_directories([config.root_dir])
        model_training_config=ModelTrainingConfig(
            root_dir=config.root_dir,
            model_path=config.model_path,
            experiment_path=config.experiment_path,
            max_seq_len=params.max_seq_len,
            d_model=params.d_model,
            lr=params.learning_rate,
            preload=config.preload,
            model_basename=config.model_basename,
            num_epochs=params.num_epochs

        )
        return model_training_config
    def get_model_translate_config(self)-> ModelTranslateConfig:
        config=self.config.data_translate
        params=self.params.modeltrainer
        print(len(params))
        
        model_translate_config=ModelTranslateConfig(
            tokenizer_file=config.tokenizer_file,
            src_lang=params.src_lang,
            tgt_lang=params.tgt_lang,
            max_seq_len=params.max_seq_len,
            model_path=config.model_path,
            model_basename=config.model_basename,
            epoch_name=config.epoch_name

        )
        return model_translate_config