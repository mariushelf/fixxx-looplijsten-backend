import logging
import os

import requests
from apps.fraudprediction.fraud_predict import FraudPredict
from celery import shared_task
from django.conf import settings

from .mock import fraud_prediction_results
from .utils import api_results_to_instances, get_case_ids_to_score

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


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def fraudpredict_vakantieverhuur(self):
    """
    Calculate fraudpredictions for vakantieverhuur
    """

    model_name = settings.FRAUD_PREDICTION_MODEL_VAKANTIEVERHUUR

    logger.info("Started fraudpredict vakantieverhuur task")
    try:
        logger.info(os.environ)
        logger.info(settings.VAKANTIEVERHUUR_HITKANS_API_BASE)
        case_ids = get_case_ids_to_score(model_name)
        logger.info("vakantieverhuur task: case id count")
        logger.info(len(case_ids))
        logger.info("vakantieverhuur task: case ids")
        logger.info(case_ids)
        logger.info("vakantieverhuur task: use mock data?")
        logger.info(settings.USE_HITKANS_MOCK_DATA)
        if settings.USE_HITKANS_MOCK_DATA:
            logger.info("vakantieverhuur task: use mock data")
            result = fraud_prediction_results()
        else:
            data = {
                "zaken_ids": get_case_ids_to_score(model_name),
                "auth_token": settings.VAKANTIEVERHUUR_HITKANS_AUTH_TOKEN,
            }

            response = requests.post(
                settings.VAKANTIEVERHUUR_HITKANS_API_BASE + "/score_zaken",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                json=data,
                headers={
                    "content-type": "application/json",
                },
            )
            response.raise_for_status()
            logger.info("vakantieverhuur task: response status")
            logger.info(response.status)
            logger.info("vakantieverhuur task: response text")
            logger.info(response.text)
            logger.info("vakantieverhuur task: response json")
            logger.info(response.json())
            result = response.json()

        api_results_to_instances(result, model_name)

        logger.info("Ended fraudpredict vakantieverhuur task")

    except Exception as exception:
        self.retry(exc=exception)

    return True
