#create entity that is return type
from dataclasses import dataclass
from pathlib import Path
#data class bhaneko class banauxa instance haru

@dataclass(frozen=True)
class DataIngestionConfig:
    root_dir: Path
    source_URL: str
    local_data_file: Path
    unzip_dir: Path  # Correctly typed and declared

@dataclass(frozen=True)
class DataValidationConfig:
    root_dir:Path
    STATUS_FILE:str
    ALL_REQUIRED_FILES:str
    
@dataclass(frozen=True)
class DataTransformConfig:
    root_dir:Path
    data_path:Path
    tokenizer_file:Path
    max_seq_len:int
    src_lang:str
    tgt_lang:str
    src_file:Path
    tgt_file:Path
    batch_size:int

@dataclass(frozen=True)
class ModelTrainingConfig:
    root_dir:Path
    model_path:Path
    experiment_path:Path
    max_seq_len:int
    d_model:int
    lr:float
    model_basename:str
    num_epochs:int
    preload:bool | str

@dataclass(frozen=True)
class ModelTranslateConfig:
    root_dir:Path
    tokenizer_file:Path
    src_lang:str
    tgt_lang:Path
    max_seq_len:int
    model_path:Path
    model_basename:Path
    epoch_name: int


