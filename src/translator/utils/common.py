import os 
import yaml
from pathlib import Path
from box.exceptions import BoxValueError
from ensure import ensure_annotations
from box import ConfigBox
from typing import Any
from translator.logging import logger


@ensure_annotations
def read_yaml(path_to_yaml:Path)->ConfigBox:
    """
    Read a YAML file and convert it into a ConfigBox.

    Args:
        path_to_yaml (Path): The path to the YAML file.

    Returns:
        ConfigBox: A ConfigBox object containing the parsed YAML data.

    Raises:
        BoxValueError: If the YAML file is not found or does not contain valid data.
    """
    try:
        with open(path_to_yaml) as yaml_file:
            content=yaml.safe_load(yaml_file)
            logger.info(f"yaml_file:{path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except BoxValueError :
        raise ValueError("Yaml file is empty")
    except Exception as e:
        raise e
    
@ensure_annotations
def create_directories(path_to_directories:list,verbose=True):
    """
    Create directories at the specified paths.

    Args:
        path_to_directoriers (list): A list of paths to directories.
        verbose (bool, optional): If True, print messages indicating the creation of directories. Defaults to True.
    """
    for directory in path_to_directories:
        os.makedirs(directory,exist_ok=True)
        if verbose:
            logger.info(f"Directory '{directory}' created successfully")

@ensure_annotations
def get_size(path:Path)-> str:
    """
    Get the size of a file in human-readable format.

    Args:
        path (Path): The path to the file.

    Returns:
        str: The size of the file in human-readable format.
    """
    size_in_kb=round(os.path.getsize(path)/1024)
    return f"{size_in_kb} KB"