# TODO: Add tests
import logging
import os
from datetime import datetime
from multiprocessing import Process

from apps.fraudprediction.fraud_predict import FraudPredict
from apps.fraudprediction.permissions import FraudPredictionApiKeyAuth
from django import db
from django.conf import settings
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from .utils import fraudpredict_vakantieverhuur

LOGGER = logging.getLogger(__name__)


class FraudPredictionScoringViewSet(ViewSet):
    """
    A view for triggering fraud scoring
    """

    permission_classes = [FraudPredictionApiKeyAuth | IsAuthenticated]

    def background_process(self):
        LOGGER.info("Started scoring background process")

        if hasattr(os, "getppid"):
            LOGGER.info("Scoring process: {}".format(os.getpid()))

        fraud_predict = FraudPredict(
            model_name=settings.FRAUD_PREDICTION_MODEL_ONDERHUUR,
            score_module_path="onderhuur_prediction_model.score",
        )
        fraud_predict.start()

        LOGGER.info("Finished scoring background process")

    def create(self, request):
        if hasattr(os, "getppid"):
            LOGGER.info("Process kicking off scoring: {}".format(os.getpid()))

        model = request.GET.get("model", settings.FRAUD_PREDICTION_MODEL_ONDERHUUR)

        if model == settings.FRAUD_PREDICTION_MODEL_ONDERHUUR:
            db.connections.close_all()
            p = Process(target=self.background_process)
            p.start()
        else:
            fraudpredict_vakantieverhuur()

        json = {
            "message": "Scoring Started {}".format(str(datetime.now())),
        }
        return JsonResponse(json)
