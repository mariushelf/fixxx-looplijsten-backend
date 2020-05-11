import logging

from api.fraudprediction.models import FraudPrediction
from api.fraudprediction.serializers import FraudPredictionSerializer

LOGGER = logging.getLogger(__name__)


def get_fraud_prediction(case_id):
    try:
        fraud_prediction = FraudPrediction.objects.get(case_id=case_id)
        serializer = FraudPredictionSerializer(fraud_prediction)
        return serializer.data
    except FraudPrediction.DoesNotExist:
        LOGGER.warning('Fraud prediction object for case does not exist: {}'.format(case_id))


def get_fraud_predictions():
    '''
    Returns a dictionary of all fraud predictions mapped to case_ids
    '''
    fraud_predictions = FraudPrediction.objects.all()
    fraud_prediction_dictionary = {}

    for fraud_prediction in fraud_predictions:
        fraud_prediction_dictionary[fraud_prediction.case_id] = FraudPredictionSerializer(
            fraud_prediction).data

    return fraud_prediction_dictionary


def add_fraud_predictions(cases):
    '''
    Returns a list of case dictionaries, enriched with fraud_predictions
    '''
    cases = cases.copy()

    for case in cases:
        case_id = case.get('case_id')
        case['fraud_prediction'] = get_fraud_prediction(case_id)

    return cases
