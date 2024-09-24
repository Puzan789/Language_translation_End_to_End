import os 
import logging
import sys

logging_str="[%(asctime)s:%(levelname)s:%(module)s:%(message)s"
log_dir="logs"
log_filepath=os.path.join(log_dir,"running_logs.log")
os.makedirs(log_dir,exist_ok=True)

#configuring the logging settings

logging.basicConfig(
    level=logging.INFO, #set the logging level to INFO , This will capture INFO,WARNING,ERROR and CRITICAL LOGS.
    format=logging_str, #set the format of the log messages
    handlers=[
        logging.FileHandler(log_filepath), #set the log file handler to log_filepath
        logging.StreamHandler(sys.stdout) #set the log stream handler to print the logs in the console
    ]
    )
logger=logging.getLogger("languageTranslatorLogger")