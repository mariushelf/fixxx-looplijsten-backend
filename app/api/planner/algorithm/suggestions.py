import logging

from api.fraudprediction.utils import get_fraud_prediction
from api.planner.algorithm.base import ItineraryGenerateAlgorithm
from api.planner.const import MAX_SUGGESTIONS_COUNT
from api.planner.utils import calculate_geo_distances

LOGGER = logging.getLogger(__name__)

class ItineraryGenerateSuggestions(ItineraryGenerateAlgorithm):
    ''' Generates a list of suggestion based on a given location '''

    def generate(self, location):

        cases = self.__get_eligible_cases__()

        if not cases:
            LOGGER.warning('No eligible cases, could not generate suggestions')
            return []

        # Calculate a list of distances for each case
        center = (location['lat'], location['lng'])
        distances = calculate_geo_distances(center, cases)

        # Add the distances and fraud predictions to the cases
        for index, case in enumerate(cases):
            case['distance'] = distances[index]
            case['fraud_prediction'] = get_fraud_prediction(case['case_id'])

        # Sort the cases based on distance
        sorted_cases = sorted(cases, key=lambda case: case['distance'])[:MAX_SUGGESTIONS_COUNT]
        return sorted_cases
