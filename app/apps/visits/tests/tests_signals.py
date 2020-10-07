"""
Tests for helpers
"""
from datetime import datetime

from apps.cases.models import Case
from apps.itinerary.models import Itinerary, ItineraryItem
from apps.users.models import User
from apps.visits.models import Visit, VisitMetaData
from apps.visits.signals import capture_visit_meta_data, post_save_visit
from django.db.models import signals
from django.test import TestCase
from pytz import UTC


class VisitsSignalsTests(TestCase):
    def get_mock_case(self):
        case = Case.get("FOO Case ID")
        return case

    def get_mock_case_with_fraud_prediction(self):
        case = Case.get("FOO Case ID")
        # TODO: Add fraud prediction
        return case

    def get_mock_visit(self, case):
        """
        Utility function to generate mock Visit object to test with
        """
        # First create a mock Visit object
        itinerary = Itinerary.objects.create()
        case = Case.get("FOO Case ID")
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary, case=case)
        user = User.objects.create(email="foo_a@foo.com")

        visit = Visit.objects.create(
            author=user,
            itinerary_item=itinerary_item,
            start_time=datetime(2020, 10, 6, tzinfo=UTC),
        )

        return visit

    def test_if_signal_is_connected(self):
        """
        Tests if the signal to capture visit data is connected
        """
        registered_functions = [
            receiver[1]() for receiver in signals.post_save.receivers
        ]
        self.assertIn(post_save_visit, registered_functions)

    def test_visit_meta_data_creation(self):
        """
        Tests if the signal helper function (capture_visit_meta_data) creates VisitMetaData
        """
        self.assertEquals(VisitMetaData.objects.count(), 0)
        case = self.get_mock_case()
        visit = self.get_mock_visit(case)
        capture_visit_meta_data(visit)
        self.assertEquals(VisitMetaData.objects.count(), 1)

    def test_visit_single_meta_data(self):
        """
        Only one VisitMetaData can be created for a visit and signal
        """
        case = self.get_mock_case()
        visit = self.get_mock_visit(case)
        capture_visit_meta_data(visit)
        self.assertEquals(VisitMetaData.objects.count(), 1)

        capture_visit_meta_data(visit)
        self.assertEquals(VisitMetaData.objects.count(), 1)
