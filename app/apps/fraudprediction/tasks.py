import logging

from apps.fraudprediction.fraud_predict import FraudPredict
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_RETRY_DELAY = 10
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 60


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def fraudpredict(self):
    """
    Calculate fraudpredictions per type
    """

    try:
        logger.info("Started fraudpredict task")
        fraud_predict = FraudPredict(
            model_name=settings.FRAUD_PREDICTION_MODEL_VAKANTIEVERHUUR,
            score_module_path="woonfraude_model.score",
        )
        fraud_predict.start()
        logger.info("Ended fraudpredict task")

        return True
    except Exception as exception:
        self.retry(exc=exception)


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def fraudpredict_onderhuur(self):
    """
    Calculate fraudpredictions per type
    """

    try:
        logger.info("Started fraudpredict onderhuur task")
        fraud_predict = FraudPredict(
            model_name=settings.FRAUD_PREDICTION_MODEL_ONDERHUUR,
            score_module_path="onderhuur_prediction_model.score",
        )
        fraud_predict.start()
        logger.info("Ended fraudpredict onderhuur task")

    except Exception as exception:
        self.retry(exc=exception)

    return True
