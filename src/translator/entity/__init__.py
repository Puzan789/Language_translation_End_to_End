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
