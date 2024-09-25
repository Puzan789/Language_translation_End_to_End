from translator.pipeline.stage_01_dataingestion import DataIngestionTrainingPipeline
from translator.logging import logger

STAGE_NAME="DATA INGESTION STAGE"
try:
    logger.info (f"<><><><>{STAGE_NAME} Started <><><><>")
    data_ingestion =DataIngestionTrainingPipeline()
    data_ingestion.main()
    logger.info(f"<><><> stage {STAGE_NAME} completed successfully <><><>")
except Exception as e:
    logger.exception(e)
    raise e
