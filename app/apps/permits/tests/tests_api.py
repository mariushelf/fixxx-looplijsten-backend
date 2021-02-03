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


class PermitViewSetTest(APITestCase):
    """
    Tests for the API endpoints for retrieving permit data
    """

    MOCK_BAG_ID = "0363010000809805"
    PERMIT_URL_NAME = "all-permits-permit checkmarks"

    def _get_url(self):
        return "%s?bag_id=%s" % (
            reverse(self.PERMIT_URL_NAME),
            self.MOCK_BAG_ID,
        )

    def test_unauthenticated_request(self):
        """
        An unauthenticated request should not be possible
        """

        url = self._get_url()
        client = get_unauthenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_requests_no_bag_id(self):
        """
        An authenticated request fails if the requested id's doesn't have a bag_id
        """

        url = reverse(self.PERMIT_URL_NAME)
        client = get_authenticated_client()
        response = client.get(url)

        # The response returns a 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.permits.views.DecosJoinRequest.get_checkmarks_by_bag_id")
    def test_authenticated_requests_succeeds(self, mock_get_checkmarks_by_bag_id):
        """
        An authenticated request succeeds and contains all the necessary data
        """

        MOCK_RESPONSE = {
            "has_b_and_b_permit": "UNKNOWN",
            "has_vacation_rental_permit": "UNKNOWN",
            "has_splitsing_permit": "UNKNOWN",
            "has_ontrekking_vorming_samenvoeging_permit": "UNKNOWN",
            "has_omzettings_permit": "UNKNOWN",
            "has_ligplaats_permit": "UNKNOWN",
        }
        mock_get_checkmarks_by_bag_id.return_value = MOCK_RESPONSE

        url = self._get_url()
        client = get_authenticated_client()
        response = client.get(url)

        # The response returns a 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEquals(response.json(), MOCK_RESPONSE)
