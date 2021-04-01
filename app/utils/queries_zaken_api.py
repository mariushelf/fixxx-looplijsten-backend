# TODO: Tests for this
import logging
from datetime import datetime

import requests
from django.conf import settings
from tenacity import after_log, retry, stop_after_attempt, wait_random
from utils.queries import get_case, get_import_stadia
from utils.queries_bag_api import get_bag_id

logger = logging.getLogger(__name__)


def get_headers(auth_header=None):
    token = settings.SECRET_KEY_TOP_ZAKEN
    headers = {
        "Authorization": f"{auth_header}" if auth_header else f"{token}",
        "content-type": "application/json",
    }
    return headers


def date_to_string(date):
    if date:
        return str(date)

    return None


def stadium_bwv_to_push_state(stadium):
    """ Transforms a stadium to be compatible with zaken-backend """
    return {
        "name": stadium.get("sta_oms"),
        "start_date": date_to_string(stadium.get("begindatum")),
        "end_date": date_to_string(stadium.get("einddatum", None)),
        "gauge_date": date_to_string(stadium.get("peildatum", None)),
        "invoice_identification": stadium.get("invordering_identificatie"),
    }


def assert_allow_push():
    assert settings.ZAKEN_API_URL, "ZAKEN_API_URL is not configured in settings."
    assert settings.PUSH_ZAKEN, "Pushes disabled"
