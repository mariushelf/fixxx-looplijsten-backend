import datetime
from unittest.mock import Mock, patch

from apps.cases.models import Case
from apps.fraudprediction.models import FraudPrediction
from apps.fraudprediction.serializers import FraudPredictionSerializer
from apps.itinerary.models import ItineraryItem
from apps.visits.models import Visit
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase
from settings.const import ISSUEMELDING

from app.utils.unittest_helpers import (
    get_authenticated_client,
    get_unauthenticated_client,
)


class CaseViewSetTest(APITestCase):
    """
    Tests for the API endpoints for retrieving case data
    """

    def test_unauthenticated_request(self):
        """
        An unauthenticated request should not be possible
        """

        url = reverse("v1:case-detail", kwargs={"pk": "foo"})
        client = get_unauthenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("apps.cases.views.brk_api")
    @patch("apps.cases.views.bag_api")
    @patch("apps.cases.views.q")
    def test_authenticated_requests_no_case(self, mock_q, mock_bag_api, mock_brk_api):
        """
        An authenticated request fails if the requested id's doesn't have a wng_id or adres_id
        """

        mock_q.get_related_case_ids.return_value = {}

        MOCK_CASE_ID = "FOO_ID"
        url = reverse("v1:case-detail", kwargs={"pk": MOCK_CASE_ID})
        client = get_authenticated_client()
        response = client.get(url)

        # Makes sure the get_related_case_ids was called using the given pk
        mock_q.get_related_case_ids.assert_called_with(MOCK_CASE_ID)

        # The response returns a 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TODO: Add test that also includes team_settings in the case detail data
    @patch("apps.cases.views.get_fraud_prediction")
    @patch("apps.cases.views.brk_api")
    @patch("apps.cases.views.bag_api")
    @patch("apps.cases.views.q")
    def test_authenticated_requests_succeeds(
        self, mock_q, mock_bag_api, mock_brk_api, mock_fraud_prediction
    ):
        """
        An authenticated request succeeds and contains all the necessary data
        """

        mock_q.get_related_case_ids.return_value = {
            "wng_id": "FOO_WNG_D",
            "adres_id": "FOO_ADRES_ID",
        }

        FOO_BAG_DATA = {"verblijfsobjectidentificatie": "FOO_BAG_DATA_ID"}
        mock_bag_api.get_bag_data = Mock(return_value=FOO_BAG_DATA)

        FOO_BWV_HOTLINE_BEVINDINGEN = "FOO_BWV_HOTLINE_BEVINDINGEN"
        mock_q.get_bwv_hotline_bevinding = Mock(
            return_value=FOO_BWV_HOTLINE_BEVINDINGEN
        )

        FOO_BWV_HOTLINE_MELDING = "FOO_BWV_HOTLINE_MELDING"
        mock_q.get_bwv_hotline_melding = Mock(return_value=FOO_BWV_HOTLINE_MELDING)

        FOO_BWV_PERSONEN = "FOO_BWV_PERSONEN"
        mock_q.get_bwv_personen = Mock(return_value=FOO_BWV_PERSONEN)

        FOO_IMPORT_ADRES = "FOO_IMPORT_ADRES"
        mock_q.get_import_adres = Mock(return_value=FOO_IMPORT_ADRES)

        FOO_IMPORT_STADIA = "FOO_IMPORT_STADIA"
        mock_q.get_import_stadia = Mock(return_value=FOO_IMPORT_STADIA)

        FOO_BWV_TEMP = "FOO_BWV_TEMP"
        mock_q.get_bwv_tmp = Mock(return_value=FOO_BWV_TEMP)

        FOO_STATEMENTS = "FOO_STATEMENTS"
        mock_q.get_statements = Mock(return_value=FOO_STATEMENTS)

        FOO_RENTAL_INFORMATION = "FOO_RENTAL_INFORMATION"
        mock_q.get_rental_information = Mock(return_value=FOO_RENTAL_INFORMATION)

        FOO_RELATED_CASES = "FOO_RELATED_CASES"
        mock_q.get_related_cases = Mock(return_value=FOO_RELATED_CASES)

        FOO_BRK_DATA = "FOO_BRK_DATA"
        mock_brk_api.get_brk_data = Mock(return_value=FOO_BRK_DATA)

        # Mock the fraud prediction
        FOO_FRAUD_PREDICTION_DATA = {
            "FOO_FRAUD_PREDICTION": "FOO_FRAUD_PREDICTION_DATA"
        }
        mock_fraud_prediction.return_value = FOO_FRAUD_PREDICTION_DATA

        # Now that everythign is mocked, do the actual request
        MOCK_CASE_ID = "FOO_ID"
        url = reverse("v1:case-detail", kwargs={"pk": MOCK_CASE_ID})
        client = get_authenticated_client()
        response = client.get(url)

        # The response returns a 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The expected response with all the mocked return data
        expected_response = {
            "bwv_hotline_bevinding": FOO_BWV_HOTLINE_BEVINDINGEN,
            "bwv_hotline_melding": FOO_BWV_HOTLINE_MELDING,
            "bwv_personen": FOO_BWV_PERSONEN,
            "address": FOO_IMPORT_ADRES,
            "import_stadia": FOO_IMPORT_STADIA,
            "bwv_tmp": FOO_BWV_TEMP,
            "fraud_prediction": FOO_FRAUD_PREDICTION_DATA,
            "statements": FOO_STATEMENTS,
            "vakantie_verhuur": FOO_RENTAL_INFORMATION,
            "bag_data": FOO_BAG_DATA,
            "brk_data": FOO_BRK_DATA,
            "related_cases": FOO_RELATED_CASES,
            "day_settings_id": None,
            "is_sia": None,
        }

        self.assertEquals(response.json(), expected_response)

    def test_get_all_visits_timeline(self):
        datetime_now = datetime.datetime.now()
        datetime_future = datetime.datetime.now() + datetime.timedelta(hours=1)

        case = baker.make(Case, case_id="test")

        itinerary_item = baker.make(ItineraryItem, case=case)
        baker.make(
            Visit, itinerary_item=itinerary_item, start_time=datetime_now, case_id=case
        )
        baker.make(
            Visit,
            itinerary_item=itinerary_item,
            start_time=datetime_future,
            case_id=case,
        )

        url = reverse("v1:case-visits", kwargs={"pk": case.case_id})
        client = get_authenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_ordering_get_all_visits_timeline(self):
        datetime_now = datetime.datetime.now()
        datetime_future = datetime.datetime.now() + datetime.timedelta(hours=1)

        case = baker.make(Case, case_id="test")
        itinerary_item = baker.make(ItineraryItem, case=case)
        visit_1 = baker.make(
            Visit, itinerary_item=itinerary_item, start_time=datetime_now, case_id=case
        )
        visit_2 = baker.make(
            Visit,
            itinerary_item=itinerary_item,
            start_time=datetime_future,
            case_id=case,
        )

        url = reverse("v1:case-visits", kwargs={"pk": case.case_id})
        client = get_authenticated_client()
        response = client.get(url)
        self.assertEqual(response.json()[0]["id"], visit_2.id)
        self.assertEqual(response.json()[1]["id"], visit_1.id)


# TODO: tests for search with streetName
class CaseSearchViewSetTest(APITestCase):
    """
    Tests for the API endpoint for searching cases
    """

    MOCK_SEARCH_QUERY_PARAMETERS = {
        "postalCode": "FOO_POSTAL_CODE",
        "streetNumber": "FOO_STREET_NUMBER",
        "suffix": "FOO_SUFFIX",
        "streetName": "FOO_STREET_NAME",
    }

    def test_unauthenticated_request(self):
        """
        An unauthenticated search should not be possible
        """
        url = reverse("v1:search-list")
        client = get_unauthenticated_client()
        response = client.get(url, self.MOCK_SEARCH_QUERY_PARAMETERS)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("apps.cases.views.q")
    def test_search_without_postal_code(self, mock_q):
        """
        An authenticated search should fail if postal code and street number are not available
        """
        url = reverse("v1:search-list")
        client = get_authenticated_client()

        MOCK_SEARCH_QUERY_PARAMETERS = self.MOCK_SEARCH_QUERY_PARAMETERS.copy()
        MOCK_SEARCH_QUERY_PARAMETERS.pop("postalCode")
        MOCK_SEARCH_QUERY_PARAMETERS.pop("streetNumber")

        # Mock search function
        mock_q.get_search_results = Mock()
        mock_q.get_search_results.return_value = []

        response = client.get(url, MOCK_SEARCH_QUERY_PARAMETERS)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.cases.views.q")
    def test_search_without_street_number(self, mock_q):
        """
        An authenticated search should fail if street number is not available
        """
        url = reverse("v1:search-list")
        client = get_authenticated_client()

        MOCK_SEARCH_QUERY_PARAMETERS = self.MOCK_SEARCH_QUERY_PARAMETERS.copy()
        MOCK_SEARCH_QUERY_PARAMETERS.pop("streetNumber")

        # Mock search function
        mock_q.get_search_results = Mock()
        mock_q.get_search_results.return_value = []

        response = client.get(url, MOCK_SEARCH_QUERY_PARAMETERS)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.cases.views.q")
    def test_search_without_street_name_and_postal_code(self, mock_q):
        """
        An authenticated search should fail if street name and postal code are not available
        """
        url = reverse("v1:search-list")
        client = get_authenticated_client()

        MOCK_SEARCH_QUERY_PARAMETERS = self.MOCK_SEARCH_QUERY_PARAMETERS.copy()
        MOCK_SEARCH_QUERY_PARAMETERS.pop("streetName")
        MOCK_SEARCH_QUERY_PARAMETERS.pop("postalCode")

        # Mock search function
        mock_q.get_search_results = Mock()
        mock_q.get_search_results.return_value = []

        response = client.get(url, MOCK_SEARCH_QUERY_PARAMETERS)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.cases.views.q")
    def test_search(self, mock_q):
        """
        An authenticated search works
        """
        url = reverse("v1:search-list")
        client = get_authenticated_client()

        # Mock search function
        FOO_SEARCH_RESULTS = []
        mock_q.get_search_results = Mock(return_value=FOO_SEARCH_RESULTS)

        response = client.get(url, self.MOCK_SEARCH_QUERY_PARAMETERS)

        # Tests if the search function was called with all the given parameters
        mock_q.get_search_results.assert_called_with(
            *self.MOCK_SEARCH_QUERY_PARAMETERS.values()
        )

        # Tests if a success response code is given
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Tests if the response contains the mock data
        self.assertEqual(response.json(), {"cases": FOO_SEARCH_RESULTS})

    @patch("apps.cases.views.q")
    def test_search_without_suffix(self, mock_q):
        """
        An authenticated search works without optional suffix
        """
        url = reverse("v1:search-list")
        client = get_authenticated_client()

        # Mock search function
        FOO_SEARCH_RESULTS = []
        mock_q.get_search_results = Mock(return_value=FOO_SEARCH_RESULTS)

        MOCK_SEARCH_QUERY_PARAMETERS = self.MOCK_SEARCH_QUERY_PARAMETERS.copy()
        MOCK_SEARCH_QUERY_PARAMETERS.pop("suffix")

        response = client.get(url, MOCK_SEARCH_QUERY_PARAMETERS)

        # Tests if the search function was called with all the given parameters
        MOCK_SEARCH_QUERY_PARAMETERS_ASSERT = self.MOCK_SEARCH_QUERY_PARAMETERS.copy()
        MOCK_SEARCH_QUERY_PARAMETERS_ASSERT["suffix"] = ""
        mock_q.get_search_results.assert_called_with(
            *MOCK_SEARCH_QUERY_PARAMETERS_ASSERT.values()
        )

        # Tests if a success response code is given
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Tests if the response contains the mock data
        self.assertEqual(response.json(), {"cases": FOO_SEARCH_RESULTS})

    @patch("apps.cases.views.q")
    def test_search_with_teams_array(self, mock_q):
        """
        The cases in a search result should contain a teams array
        """
        url = reverse("v1:search-list")
        client = get_authenticated_client()

        CASE_ID = "FOO-ID"

        # Mock search function
        FOO_SEARCH_RESULTS = [{"case_id": CASE_ID}]
        mock_q.get_search_results = Mock(return_value=FOO_SEARCH_RESULTS)

        response = client.get(url, self.MOCK_SEARCH_QUERY_PARAMETERS)

        # Tests if the response contains the mock data with an added teams array
        expected_response = {
            "cases": [{"case_id": CASE_ID, "fraud_prediction": None, "teams": []}]
        }
        self.assertEqual(response.json(), expected_response)

    @patch("apps.cases.views.q")
    def test_search_with_fraud_prediction(self, mock_q):
        """
        The cases in a search result should contain a fraud_prediction if it's available
        """
        url = reverse("v1:search-list")
        client = get_authenticated_client()

        CASE_ID = "FOO-ID"

        # Mock search function
        FOO_SEARCH_RESULTS = [{"id": CASE_ID}]
        mock_q.get_search_results = Mock(return_value=FOO_SEARCH_RESULTS)

        # Create a fraud prediction object with the same CASE_ID
        fraud_prediction = FraudPrediction.objects.create(
            case_id=CASE_ID,
            fraud_probability=0.6,
            fraud_prediction=True,
            business_rules={},
            shap_values={},
        )

        response = client.get(url, self.MOCK_SEARCH_QUERY_PARAMETERS)

        expected_fraud_prediction = FraudPredictionSerializer(fraud_prediction).data
        fraud_prediction_response = (
            response.json().get("cases")[0].get("fraud_prediction")
        )

        self.assertEqual(expected_fraud_prediction, fraud_prediction_response)


class UnplannedCasesTest(APITestCase):
    """
    Tests for the API endpoint for retrieving unplanned cases
    """

    def test_unauthenticated_request(self):
        """
        An unauthenticated request should not be possible
        """

        url = reverse("v1:case-unplanned")
        client = get_unauthenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_without_date(self):
        """
        An authenticated request should fail if no date is given
        """
        url = reverse("v1:case-unplanned")
        client = get_authenticated_client()

        response = client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_stadium(self):
        """
        An authenticated request should fail if no stadium is given
        """
        url = reverse("v1:case-unplanned")
        client = get_authenticated_client()

        response = client.get(url, {"date": "2020-04-05"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_wrong_date_format(self):
        """
        An authenticated request should fail if unknown stadium is given
        """
        url = reverse("v1:case-unplanned")
        client = get_authenticated_client()

        response = client.get(url, {"date": "FOO", "stadium": ISSUEMELDING})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_correct_parameters(self):
        """
        An authenticated request should succeed with the right parameters
        """
        url = reverse("v1:case-unplanned")
        client = get_authenticated_client()

        response = client.get(url, {"date": "2020-04-05", "stadium": ISSUEMELDING})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_empty_list(self):
        """
        Should return an empty list if no cases are found
        """
        url = reverse("v1:case-unplanned")
        client = get_authenticated_client()

        response = client.get(url, {"date": "2020-04-05", "stadium": ISSUEMELDING})
        self.assertEqual(response.json(), {"cases": []})

    @patch("apps.cases.views.Itinerary")
    def test_with_filled_list(self, mock_itinerary_class):
        """
        Should return a list with cases (which include a fraud_prediction entry)
        """
        url = reverse("v1:case-unplanned")
        client = get_authenticated_client()

        mock_itinerary_class.get_unplanned_cases = Mock()
        mock_itinerary_class.get_unplanned_cases.return_value = [{"case_id": "foo"}]

        response = client.get(url, {"date": "2020-04-05", "stadium": ISSUEMELDING})
        self.assertEqual(
            response.json(), {"cases": [{"case_id": "foo", "fraud_prediction": None}]}
        )
