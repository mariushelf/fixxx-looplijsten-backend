import base64
import json
import logging
import re
from collections import defaultdict
from datetime import date, datetime, time

import requests
from apps.permits.mocks import (
    get_decos_join_mock_folder_fields,
    get_decos_join_mock_object_fields,
)
from apps.permits.serializers import (
    DecosJoinFolderFieldsResponseSerializer,
    DecosPermitSerializer,
)
from constance.backends.database.models import Constance
from django.conf import settings
from tenacity import after_log, retry, stop_after_attempt

logger = logging.getLogger(__name__)


def get_decos_join_constance_conf():
    settings_key = settings.CONSTANCE_DECOS_JOIN_PERMIT_VALID_CONF
    settings_conf, created = Constance.objects.get_or_create(key=settings_key)
    try:
        return json.loads(settings_conf.value)
    except Exception as e:
        logger.error("Decos Join constance conf NO JSON")
        logger.error(str(e))


class DecosJoinConf:
    PERMIT_TYPE = "permit_type"
    DECOS_JOIN_BOOK_KEY = "decos_join_book_key"
    EXPRESSION_STRING = "expression_string"
    INITIAL_DATA = "initial_data"
    FIELD_MAPPING = "field_mapping"
    default_expression = settings.DECOS_JOIN_DEFAULT_PERMIT_VALID_EXPRESSION
    default_initial_data = settings.DECOS_JOIN_DEFAULT_PERMIT_VALID_INITIAL_DATA
    default_field_mapping = settings.DECOS_JOIN_DEFAULT_FIELD_MAPPING
    conf = {}

    def add_conf(self, conf):
        new_conf = {}
        try:
            for p in conf:
                if len(p) >= 2:
                    new_conf.update(
                        {
                            p[0]: {
                                self.DECOS_JOIN_BOOK_KEY: p[0],
                                self.PERMIT_TYPE: p[1],
                                self.EXPRESSION_STRING: p[2]
                                if len(p) >= 3
                                else self.default_expression,
                                self.INITIAL_DATA: p[3]
                                if len(p) >= 4
                                else self.default_initial_data,
                                self.FIELD_MAPPING: p[4]
                                if len(p) >= 5
                                else self.default_field_mapping,
                            }
                        }
                    )
        except Exception as e:
            logger.error("Decos Join config invalid format")
            logger.error(str(e))
        if new_conf:
            self.conf = new_conf

    def get_conf_by_book_key(self, book_key):
        return self.conf.get(book_key)

    def get_book_keys(self):
        return [k for k, v in self.conf.items()]


class DecosJoinRequest:
    """
    Object to connect to decos join and retrieve permits
    """

    def get(self, path):
        url = "%s%s" % (settings.DECOS_JOIN_API, path)
        return self._process_request_to_decos_join(url)

    def _process_request_to_decos_join(self, url):
        try:
            headers = {
                "Accept": "application/itemdata",
                "content-type": "application/json",
            }
            request_params = {
                "headers": headers,
                "timeout": 30,
            }

            if settings.DECOS_JOIN_AUTH_BASE64:
                logger.info("Request to Decos using token")
                request_params["headers"].update(
                    {
                        "Authorization": f"Basic {settings.DECOS_JOIN_AUTH_BASE64}",
                    }
                )

            logger.info(url)

            response = requests.get(url, **request_params)

            logger.info(response.status_code)
            logger.info(response.text)

            return response.json()
        except requests.exceptions.Timeout:
            logger.error("Request to Decos Join timed out")
            return False
        except Exception as e:
            logger.error("Decos Join connection failed")
            logger.error(str(e))
            return False

    def get_decos_object_with_address(self, address):
        url = (
            settings.DECOS_JOIN_API
            + "items/"
            + settings.DECOS_JOIN_BOOK_KNOWN_BAG_OBJECTS
            + f"/COBJECTS?filter=SUBJECT1 eq '{address}'"
        )

        return self._process_request_to_decos_join(url)

    def get_decos_object_with_bag_id(self, bag_id):
        if not settings.USE_DECOS_MOCK_DATA:
            url = (
                settings.DECOS_JOIN_API
                + "items/"
                + settings.DECOS_JOIN_BOOK_KNOWN_BAG_OBJECTS
                + f"/COBJECTS?filter=PHONE3 eq '{bag_id}'"
            )

            return self._process_request_to_decos_join(url)
        else:
            return get_decos_join_mock_object_fields()

    def get_folders_with_object_id(self, object_id):
        url = settings.DECOS_JOIN_API + f"items/{object_id}/FOLDERS/"

        return self._process_request_to_decos_join(url)

    def get_documents_with_folder_id(self, folder_id):
        url = settings.DECOS_JOIN_API + f"items/{folder_id}/DOCUMENTS/"
        return self._process_request_to_decos_join(url)

    def _datestring_to_date(self, field_value):
        if type(field_value) == str and re.match(
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", field_value
        ):
            return datetime.timestamp(
                datetime.strptime(field_value.split("T")[0], "%Y-%m-%d")
            )
        return field_value

    def _clean_fields_objects(self, fields):
        return dict((k, self._datestring_to_date(v)) for k, v in fields.items())

    def _map_fields_on_conf_fields(self, fields, conf):
        return dict(
            (conf.get(DecosJoinConf.FIELD_MAPPING).get(k), v)
            for k, v in fields.items()
            if k in list(conf.get(DecosJoinConf.FIELD_MAPPING, {}).keys())
        )

    def _convert_datestring_to_date(self, date_string):
        if "T" in date_string:
            return datetime.strptime(date_string.split("T")[0], "%Y-%m-%d").date()
        return False

    def _get_decos_folder(self, decos_object):
        if not settings.USE_DECOS_MOCK_DATA:
            try:
                decos_object_id = decos_object["content"][0]["key"]
            except (KeyError, IndexError):
                decos_object_id = False
                response_decos_folder = False

            if decos_object_id:
                response_decos_folder = self.get_folders_with_object_id(decos_object_id)

            if response_decos_folder and response_decos_folder["count"] > 0:
                return response_decos_folder
            return False
        else:
            return get_decos_join_mock_folder_fields()

    def _check_if_permit_is_valid_conf(self, permit, conf, dt):
        permit_data = conf.get(DecosJoinConf.INITIAL_DATA, {})
        permit_data.update(self._clean_fields_objects(permit))
        permit_data.update(
            {
                "ts_now": datetime.timestamp(
                    datetime(dt.year, dt.month, dt.day, 0, 0, 0)
                ),
            }
        )
        base_str = conf.get(DecosJoinConf.EXPRESSION_STRING)
        base_str = base_str if base_str else "bool()"
        try:
            compare_str = base_str.format(**permit_data)
        except Exception as e:
            compare_str = base_str
            logger.error("Error Decos Join permit valid data mapping")
            logger.error(str(e))
            return "UNKNOWN"
        try:
            valid = eval(compare_str)
        except Exception as e:
            logger.error("Error Decos Join permit valid expression evaluation")
            logger.error(str(e))
            return "UNKNOWN"
        return valid

    def get_permits_by_bag_id(self, bag_id, dt):
        """ Get simple view of the important permits"""
        # TODO Make sure the response goes through a serializer so this doesn't break on KeyError
        response = []

        decos_join_conf_object = DecosJoinConf()
        decos_join_conf_object.add_conf(settings.DECOS_JOIN_DEFAULT_PERMIT_VALID_CONF)
        decos_join_conf_object.add_conf(get_decos_join_constance_conf())

        response_decos_obj = self.get_decos_object_with_bag_id(bag_id)

        if response_decos_obj:
            response_decos_folder = self._get_decos_folder(response_decos_obj)
            if response_decos_folder:

                for folder in response_decos_folder["content"]:
                    serializer = DecosJoinFolderFieldsResponseSerializer(
                        data=folder["fields"]
                    )

                    if serializer.is_valid():
                        parent_key = folder["fields"]["parentKey"]

                        if parent_key in decos_join_conf_object.get_book_keys():
                            data = {}
                            conf = decos_join_conf_object.get_conf_by_book_key(
                                parent_key
                            )
                            print(
                                self._map_fields_on_conf_fields(folder["fields"], conf)
                            )
                            data.update(
                                {
                                    "permit_granted": self._check_if_permit_is_valid_conf(
                                        folder["fields"], conf, dt
                                    ),
                                    "permit_type": conf.get(DecosJoinConf.PERMIT_TYPE),
                                    "raw_data": folder["fields"],
                                    "details": self._map_fields_on_conf_fields(
                                        folder["fields"], conf
                                    ),
                                    "date_from": datetime.strptime(
                                        folder["fields"]["date6"].split("T")[0],
                                        "%Y-%m-%d",
                                    ).date(),
                                }
                            )
                            permit_serializer = DecosPermitSerializer(data=data)
                            if permit_serializer.is_valid():
                                response.append(permit_serializer.data)
                            print(permit_serializer.errors)
                        else:
                            logger.error("DECOS JOIN parent key not found in config")
                            logger.info("book key: %s" % parent_key)
                            logger.info(
                                "Config keys: %s"
                                % decos_join_conf_object.get_book_keys()
                            )

                    else:
                        # assign variable so it is visible in Sentry
                        unexpected_answer = folder["fields"]
                        logger.error("DECOS JOIN serializer not valid")
                        logger.info(unexpected_answer)
                        logger.info(serializer.errors)

        return response
