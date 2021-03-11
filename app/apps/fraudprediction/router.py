from apps.fraudprediction.views import FraudPredictionScoringViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    r"fraud-prediction/scoring",
    FraudPredictionScoringViewSet,
    basename="fraud-prediction-score",
)


api_router = router.urls
