from translator.pipeline.stage_01_dataingestion import DataIngestionTrainingPipeline
from translator.logging import logger
from translator.pipeline.stage_02_datavalidation import DataValidationTrainingPipeline
from translator.pipeline.stage_03_datatransformation import DataTransformationPipeline

STAGE_NAME="DATA INGESTION STAGE"
try:
    logger.info (f"<><><><>{STAGE_NAME} Started <><><><>")
    data_ingestion =DataIngestionTrainingPipeline()
    data_ingestion.main()
    logger.info(f"<><><> {STAGE_NAME} completed successfully <><><>")
except Exception as e:
    logger.exception(e)
    raise e

STAGE_NAME="DATA VALIDATION STAGE"
try:
    logger.info (f"<><><><>{STAGE_NAME} Started <><><><>")
    data_validation =DataValidationTrainingPipeline()
    data_validation.main()
    logger.info(f"<><><>  {STAGE_NAME} completed successfully <><><>")
except Exception as e:
    logger.exception(e)
    raise e


STAGE_NAME="DATA TRANSFORMATION STAGE"
try:
    logger.info (f"<><><><>{STAGE_NAME} Started <><><><>")
    data_transformation =DataTransformationPipeline()
    data_transformation.main()
    logger.info(f"<><><>  {STAGE_NAME} completed successfully <><><>")
except Exception as e:
    logger.exception(e)
    raise e