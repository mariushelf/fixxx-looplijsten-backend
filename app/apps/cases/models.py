import datetime

import requests
from apps.fraudprediction.models import FraudPrediction
from django.conf import settings
from django.db import models
from utils.queries import get_case
from utils.queries_zaken_api import get_headers

from .mock import get_zaken_case_list


class Case(models.Model):
    class Meta:
        ordering = ["case_id"]

    """
    A simple case model
    """
    case_id = models.CharField(max_length=255, null=True, blank=False)
    is_top_bwv_case = models.BooleanField(default=True)

    def get(case_id, is_top_bwv_case=True):
        return Case.objects.get_or_create(
            case_id=case_id, defaults={"is_top_bwv_case": is_top_bwv_case}
        )[0]

    def fetch_case(self):
        url = f"{settings.ZAKEN_API_URL}/cases/{self.case_id}/"

        response = requests.get(
            url,
            timeout=5,
            headers=get_headers(),
        )
        response.raise_for_status()

        return response.json()

    def fetch_events(self):
        url = f"{settings.ZAKEN_API_URL}/cases/{self.case_id}/events/"

        response = requests.get(
            url,
            timeout=5,
            headers=get_headers(),
        )
        response.raise_for_status()

        return response.json()

    def __get_case__(self, case_id):
        if self.is_top_bwv_case:
            return get_case(case_id)
        if settings.USE_ZAKEN_MOCK_DATA:
            return dict((str(c.get("id")), c) for c in get_zaken_case_list()).get(
                case_id, {}
            )
        return self.fetch_case()

    def get_location(self):
        case_data = self.__get_case__(self.case_id)
        address = case_data.get("address")
        return {"lat": address.get("lat"), "lng": address.get("lng")}

    @property
    def data(self):
        return self.__get_case__(self.case_id)

    @property
    def itinerary(self):
        now = datetime.datetime.now()
        itinerary_items = self.cases.filter(
            itinerary__created_at__gte=datetime.datetime(now.year, now.month, now.day)
        )
        if itinerary_items:
            return itinerary_items[0].itinerary
        return None

    @property
    def day_settings(self):
        return self.itinerary.settings.day_settings if self.itinerary else None

    @property
    def fraud_prediction(self):
        fraud_prediction = FraudPrediction.objects.get(case_id=self.case_id)
        return fraud_prediction

    def __str__(self):
        if self.case_id:
            return self.case_id
        return ""


class Project(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)

    def get(name):
        return Project.objects.get_or_create(name=name)[0]

    def __str__(self):
        return self.name


class Stadium(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)

    def get(name):
        return Stadium.objects.get_or_create(name=name)[0]

    def __str__(self):
        return self.name


class StadiumLabel(models.Model):
    stadium = models.ForeignKey(
        to=Stadium,
        related_name="labels",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    label = models.CharField(
        default="sanctie",
        max_length=10,
    )

    def __str__(self):
        return "%s - %s" % (
            self.stadium,
            self.label,
        )
