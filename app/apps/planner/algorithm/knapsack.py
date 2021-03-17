import logging
import multiprocessing

import requests
from apps.cases.mock import get_zaken_case_list
from apps.fraudprediction.utils import get_fraud_predictions
from apps.planner.algorithm.base import ItineraryGenerateAlgorithm
from apps.planner.const import MAX_SUGGESTIONS_COUNT, SCORING_WEIGHTS
from apps.planner.models import Weights
from apps.planner.utils import calculate_geo_distances, remove_cases_from_list
from django.conf import settings
from joblib import Parallel, delayed
from settings.const import ISSUEMELDING
from utils.queries import get_case
from utils.queries_zaken_api import get_headers

logger = logging.getLogger(__name__)


class ItineraryKnapsackSuggestions(ItineraryGenerateAlgorithm):
    def __init__(self, settings, postal_code_settings=[], settings_weights=None):
        super().__init__(settings, postal_code_settings)

        self.weights = Weights()

        if settings_weights:
            self.weights = Weights(
                distance=settings_weights.distance,
                fraud_probability=settings_weights.fraud_probability,
                primary_stadium=settings_weights.primary_stadium,
                secondary_stadium=settings_weights.secondary_stadium,
                issuemelding=settings_weights.issuemelding,
                is_sia=settings_weights.is_sia,
            )

    def get_score(self, case):
        """
        Gets the score of the given case
        """
        distance = case["normalized_inverse_distance"]

        try:
            fraud_probability = case["fraud_prediction"].get("fraud_probability")
        except AttributeError:
            fraud_probability = 0

        stadium = case.get("stadium")
        has_primary_stadium = stadium == self.primary_stadium
        has_secondary_stadium = stadium in self.secondary_stadia
        has_issuemelding_stadium = stadium == ISSUEMELDING

        score = self.weights.score(
            distance,
            fraud_probability,
            has_primary_stadium,
            has_secondary_stadium,
            has_issuemelding_stadium,
            bool(case.get("is_sia") == "J"),
        )

        return score

    def get_center(self, location):
        return location.get("lat"), location.get("lng")

    def generate(self, location, cases=[], fraud_predictions=[]):
        if not cases:
            cases = self.__get_eligible_cases__()

        if not cases:
            return []

        if not fraud_predictions:
            fraud_predictions = get_fraud_predictions()

        # Calculate a list of distances for each case
        center = self.get_center(location)
        distances = calculate_geo_distances(center, cases)
        max_distance = max(distances)

        # Add the distances and fraud predictions to the cases
        for index, case in enumerate(cases):
            case_id = case.get("case_id", case.get("id"))
            case["distance"] = distances[index]
            case["normalized_inverse_distance"] = (
                max_distance - case["distance"]
            ) / max_distance
            case["fraud_prediction"] = fraud_predictions.get(case_id, None)
            case["score"] = self.get_score(case)

        # Sort the cases based on score
        sorted_cases = sorted(cases, key=lambda case: case["score"], reverse=True)

        return sorted_cases[:MAX_SUGGESTIONS_COUNT]


class ItineraryKnapsackList(ItineraryKnapsackSuggestions):
    def get_best_list(self, candidates):
        best_list = max(candidates, key=lambda candidate: candidate.get("score"))
        return best_list["list"]

    def is_same_address(self, case_a, case_b):
        same_street = case_a.get("address", {}).get("street_name") == case_b.get(
            "address", {}
        ).get("street_name")
        same_number = case_a.get("address", {}).get("number") == case_b.get(
            "address", {}
        ).get("number")
        return same_street and same_number

    def shorten_list(self, cases_all):
        cases_all = cases_all.copy()
        cases_all.reverse()
        cases = []

        counter = self.target_length

        while counter > 0 and len(cases_all):
            case = cases_all.pop()
            cases.append(case)
            counter -= 1

            if len(cases_all):
                next_case = cases_all[-1]

                if self.is_same_address(case, next_case):
                    counter += 1

        return cases

    def parallelized_function(self, case, cases, fraud_predictions, index):
        suggestions = super().generate(case, cases, fraud_predictions)
        cases = self.shorten_list(suggestions)

        score = sum([case["score"] for case in cases])
        return {"score": score, "list": cases}

    def generate(self):
        fraud_predictions = get_fraud_predictions()

        if self.start_case_id:
            case = get_case(self.start_case_id)
            case["fraud_prediction"] = fraud_predictions.get(self.start_case_id, None)

            suggestions = super().generate(case)
            suggestions = remove_cases_from_list(suggestions, [case])
            suggestions = suggestions[: self.target_length - 1]
            suggestions = [case] + suggestions

            return suggestions

        # If no location is given, generate all possible lists, and choose the best one
        cases = self.__get_eligible_cases__()
        if not cases:
            logger.warning("No eligible cases, could not generate best list")
            return []

        # Run in parallel processes to improve speed
        jobs = multiprocessing.cpu_count()

        # multiprocessing freezes during local sometimes, option is trying threads insteads
        # candidates = Parallel(n_jobs=jobs, prefer="threads")(

        candidates = Parallel(n_jobs=jobs, backend="multiprocessing")(
            delayed(self.parallelized_function)(case, cases, fraud_predictions, index)
            for index, case in enumerate(cases)
        )

        best_list = self.get_best_list(candidates)
        best_list = sorted(best_list, key=lambda case: case["distance"])

        return best_list


class ItineraryKnapsackListV1(ItineraryKnapsackList):
    pass


class ItineraryKnapsackListV2(ItineraryKnapsackList):
    def __get_eligible_cases__(self):
        print("v2 __get_eligible_cases__")
        if settings.USE_ZAKEN_MOCK_DATA:
            return get_zaken_case_list()

        url = f"{settings.ZAKEN_API_URL}/cases/"
        queryParams = {
            "openCases": "true",
            "team": self.settings.day_settings.team_settings.zaken_team_name,
            "startDate": self.settings.opening_date.strftime("%Y-%m-%d"),
        }

        response = requests.get(
            url,
            params=queryParams,
            timeout=0.5,
            headers=get_headers(),
        )
        response.raise_for_status()

        logger.info("zaken __get_eligible_cases__")
        logger.info(response.json())

        result = response.json()
        return result.get("results", [])
