from translator.pipeline.stage_01_dataingestion import DataIngestionTrainingPipeline
from translator.logging import logger
from translator.pipeline.stage_02_datavalidation import DataValidationTrainingPipeline
from translator.pipeline.stage_03_datatransformation import DataTransformationPipeline
from translator.pipeline.stage_04_datatraining import ModelTrainingPipeline
from translator.pipeline.stage_05_datatranslate import TranslateService

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

STAGE_NAME="MODEL TRAINING STAGE"
try:
    logger.info (f"<><><><>{STAGE_NAME} Started <><><><>")
    model_training=ModelTrainingPipeline()
    model_training.main()
    logger.info(f"<><><>  {STAGE_NAME} completed successfully <><><>")
except Exception as e:
    logger.exception(e)
    raise e

TAGE_NAME="MODEL TRANSLATION STAGE"
try:
    logger.info (f"<><><><>{STAGE_NAME} Started <><><><>")
    model_translate=TranslateService()

    sent=model_translate.translate("Our country is beautiful")
    print(f"Test sentence:{sent}")
    logger.info(f"Translated test sentence :{sent}")
    logger.info(f"<><><>  {STAGE_NAME} completed successfully <><><>")
except Exception as e:
    logger.exception(e)
    raise e