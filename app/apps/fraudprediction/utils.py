import logging
import math

from apps.cases.models import Project, Stadium
from apps.fraudprediction.models import FraudPrediction
from apps.fraudprediction.serializers import FraudPredictionSerializer
from settings.const import STARTING_FROM_DATE
from utils.queries_planner import get_cases_from_bwv

LOGGER = logging.getLogger(__name__)


def get_stadia_to_score(model_name):
    return list(
        dict.fromkeys(
            Stadium.objects.filter(
                team_settings_list__fraud_prediction_model=model_name,
                team_settings_list__use_zaken_backend=False,
            ).values_list("name", flat=True)
        )
    )


def get_projects_to_score(model_name):
    return list(
        dict.fromkeys(
            Project.objects.filter(
                team_settings_list__fraud_prediction_model=model_name,
                team_settings_list__use_zaken_backend=False,
            ).values_list("name", flat=True)
        )
    )


def get_case_ids_to_score(model_name, use_zaken_backend=False):
    """
    Returns a list of case ids which are eligible for scoring
    """
    case_ids = []
    if use_zaken_backend:
        pass
    else:
        cases = get_cases_from_bwv(
            STARTING_FROM_DATE,
            get_projects_to_score(model_name),
            get_stadia_to_score(model_name),
        )
        case_ids = list(set([case.get("id") for case in cases]))
    return case_ids


def clean_dictionary(dictionary):
    """
    Replaces dictionary NaN values with 0
    """
    dictionary = dictionary.copy()

    for key, value in dictionary.items():
        if math.isnan(value):
            dictionary[key] = 0.0

    return dictionary


def api_results_to_instances(results, model_name):
    for case_id, fraud_prediction in results.get("prediction_woonfraude", {}).items():
        FraudPrediction.objects.update_or_create(
            case_id=case_id,
            defaults={
                "fraud_prediction_model": model_name,
                "fraud_probability": results.get("prob_woonfraude", {}).get(case_id, 0),
                "fraud_prediction": fraud_prediction,
                "business_rules": clean_dictionary(
                    results.get("business_rules", {}).get(case_id, {})
                ),
                "shap_values": clean_dictionary(
                    results.get("shap_values", {}).get(case_id, {})
                ),
            },
        )


def get_fraud_prediction(case_id):
    try:
        fraud_prediction = FraudPrediction.objects.get(case_id=case_id)
        serializer = FraudPredictionSerializer(fraud_prediction)
        return serializer.data
    except FraudPrediction.DoesNotExist:
        LOGGER.warning(
            "Fraud prediction object for case does not exist: {}".format(case_id)
        )


def get_fraud_predictions():
    """
    Returns a dictionary of all fraud predictions mapped to case_ids
    """
    fraud_predictions = FraudPrediction.objects.all()
    fraud_prediction_dictionary = {}

    for fraud_prediction in fraud_predictions:
        fraud_prediction_dictionary[
            fraud_prediction.case_id
        ] = FraudPredictionSerializer(fraud_prediction).data

    return fraud_prediction_dictionary


def add_fraud_predictions(cases):
    """
    Returns a list of case dictionaries, enriched with fraud_predictions
    """
    cases = cases.copy()

    for case in cases:
        case_id = case.get("id")
        case["fraud_prediction"] = get_fraud_prediction(case_id)

    return cases
