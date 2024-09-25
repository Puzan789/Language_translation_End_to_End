#components 
import os 
import urllib.request as request
import zipfile
from translator.logging import logger
from translator.utils import common
from translator.entity import DataIngestionConfig
from translator.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH
from translator.utils.common import read_yaml,create_directories,get_size



class Dataingestion:
    def __init__(self,config:DataIngestionConfig):
        self.config=config
    
    def download_file(self):
        if not self.config.local_data_file.exists() or os.path.getsize(self.config.local_data_file)==0:
            try:
                file_name,header=request.urlretrieve(
                    url=self.config.source_URL,
                    filename=self.config.local_data_file
                )
                logger.info(f"{file_name} downloaded with the following {header}")
                #verifying whether the file is empty or not
                if os.path.getsize(self.config.local_data_file)==0:
                    logger.error("Download file is empty.")
                    raise Exception ("Empty downloaded file")
            except Exception as e :
                raise f"Error occured while downloading the file {e}"
        else:
            logger.info (f"file already exists with the size {get_size(self.config.local_data_file)}")
    
    def extract_zip_file(self):
        unzip_path=self.config.unzip_dir
        os.makedirs(unzip_path,exist_ok=True)
        logger.info(f"Extracting zip file to {unzip_path}")
        try :
            with zipfile.ZipFile(self.config.local_data_file,'r') as zip_f:
                zip_f.extractall(unzip_path)
                logger.info("Extraction completed successfully")
        except zipfile.BadZipFile:
            logger.error(f"Bad zip file {self.config.local_data_file}")
        except zipfile.LargeZipFile:
            logger.error(f"Zip file too large{self.config.local_data_file}")
        except Exception as e:
            logger.error(f"Error occured while extracting zip file {e}")
            raise
            
        
    

