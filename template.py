import os 
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO,format='[%(asctime)s]:%(message)s')

project_name="translator"
api_project_name="translatorapi"

list_of_files=[
    f"src/{project_name}/__init__.py",
    f"src/{project_name}/components/__init__.py",
    f"src/{project_name}/utils/__init__.py",
    f"src/{project_name}/utils/common.py",
    f"src/{project_name}/logging/__init__.py",
    f"src/{project_name}/config/__init__.py",
    f"src/{project_name}/config/configuration.py",
    f"src/{project_name}/pipeline/__init__.py",
    f"src/{project_name}/entity/__init__.py",
    f"src/{project_name}/constants/__init__.py",
    "config/config.yaml",
    "param/params.yaml",
    "tests/transformer_tests/translator_test.py",
    "tests/api_tests/api_test.py",
    f"src/{api_project_name}/main.py",
    f"src/{api_project_name}/dependencies.py"
]

for filepath in list_of_files:
    #convert the string path into a Path object
    filepath=Path(filepath)

    #spiltting the path into directory and filename
    filedir,filename=os.path.split(filepath)

    #checking the directory path is empty or not
    if filedir !="":
        #creating the directory if it does not exist
        os.makedirs(filedir,exist_ok=True)
        logging.info(f"Created directory: {filedir}")
    
    if (not os.path.exists(filepath))or (os.path.getsize(filepath==0)):
        #create an empty file
        with open(filepath,"w") as f:
            pass #just creating the file no content is written
        logging.info(f"Created file: {filepath}")
    else:
        # If the file already exists and is not empty log the information
        logging.info(f"File: {filepath} already exists.")

