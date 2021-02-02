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
    FIELD_NAME = "field_name"
    DECOS_JOIN_BOOK_KEY = "decos_join_book_key"
    EXPRESSION_STRING = "expression_string"
    INITIAL_DATA = "initial_data"
    default_expression = settings.DECOS_JOIN_DEFAULT_PERMIT_VALID_EXPRESSION
    default_initial_data = settings.DECOS_JOIN_DEFAULT_PERMIT_VALID_INITIAL_DATA
    conf = {}
    valid_permits = [
        "has_b_and_b_permit",
        "has_vacation_rental_permit",
        "has_omzettings_permit",
        "has_splitsing_permit",
        "has_ontrekking_vorming_samenvoeging_permit",
        "has_ligplaats_permit",
    ]

    def add_conf(self, conf):
        new_conf = {}
        try:
            for p in conf:
                if len(p) >= 2 and p[1] in self.valid_permits:
                    new_conf.update(
                        {
                            p[0]: {
                                self.DECOS_JOIN_BOOK_KEY: p[0],
                                self.FIELD_NAME: p[1],
                                self.EXPRESSION_STRING: p[2]
                                if len(p) >= 3
                                else self.default_expression,
                                self.INITIAL_DATA: p[3]
                                if len(p) >= 4
                                else self.default_initial_data,
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

    def _check_if_permit_is_valid(self, permit):
        premit_date_granted = self._convert_datestring_to_date(permit["date5"])
        permit_status = permit["dfunction"]
        permit_from_date = self._convert_datestring_to_date(permit["date6"])

        if "date7" in permit:
            permit_untill_date = self._convert_datestring_to_date(permit["date7"])

            if (
                permit_from_date
                and premit_date_granted
                and permit_from_date <= datetime.today().date()
                and permit_untill_date >= datetime.today().date()
                and premit_date_granted <= datetime.today().date()
                and permit_status == "Verleend"
            ):
                return True
        else:
            if (
                premit_date_granted
                and premit_date_granted <= datetime.today().date()
                and permit_from_date <= datetime.today().date()
                and permit_status == "Verleend"
            ):
                return True

        # Check if permit is valid today and has been granted

        return False

    def _check_if_permit_is_valid_conf(self, permit, conf):
        now = datetime.today()
        permit_data = conf.get(DecosJoinConf.INITIAL_DATA, {})
        permit_data.update(self._clean_fields_objects(permit))
        permit_data.update(
            {
                "ts_now": datetime.timestamp(
                    datetime(now.year, now.month, now.day, 0, 0, 0)
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
        try:
            valid = eval(compare_str)
        except Exception as e:
            logger.error("Error Decos Join permit valid expression evaluation")
            logger.error(str(e))
            return False
        return valid

    def get_checkmarks_by_bag_id(self, bag_id):
        """ Get simple view of the important permits"""
        # TODO Make sure the response goes through a serializer so this doesn't break on KeyError
        response = {
            "has_b_and_b_permit": "UNKNOWN",
            "has_vacation_rental_permit": "UNKNOWN",
            "has_splitsing_permit": "UNKNOWN",
            "has_ontrekking_vorming_samenvoeging_permit": "UNKNOWN",
            "has_omzettings_permit": "UNKNOWN",
            "has_ligplaats_permit": "UNKNOWN",
        }
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
                        # print(folder)
                        # print(parent_key in decos_join_conf_object.get_book_keys())
                        if parent_key in decos_join_conf_object.get_book_keys():
                            conf = decos_join_conf_object.get_conf_by_book_key(
                                parent_key
                            )
                            response[
                                conf.get(DecosJoinConf.FIELD_NAME)
                            ] = self._check_if_permit_is_valid_conf(
                                folder["fields"], conf
                            )
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

    def get_permits_by_bag_id(self, bag_id):
        response_decos_obj = self.get_decos_object_with_bag_id(bag_id)
        permits = []

        if response_decos_obj:
            response_decos_folder = self._get_decos_folder(response_decos_obj)

            if response_decos_folder:
                for folder in response_decos_folder["content"]:
                    serializer = DecosJoinFolderFieldsResponseSerializer(
                        data=folder["fields"]
                    )

                    if serializer.is_valid():
                        ser_data = {
                            "permit_granted": self._check_if_permit_is_valid(
                                folder["fields"]
                            ),
                            "processed": folder["fields"]["dfunction"],
                            "date_from": datetime.strptime(
                                folder["fields"]["date6"].split("T")[0], "%Y-%m-%d"
                            ).date(),
                        }
                        parent_key = folder["fields"]["parentKey"]

                        if "date7" in folder["fields"]:
                            ser_data["date_to"] = datetime.strptime(
                                folder["fields"]["date7"].split("T")[0], "%Y-%m-%d"
                            ).date()

                        if parent_key == settings.DECOS_JOIN_BANDB_ID:
                            ser_data[
                                "permit_type"
                            ] = DecosPermitSerializer.PERMIT_B_AND_B
                        elif parent_key == settings.DECOS_JOIN_VAKANTIEVERHUUR_ID:
                            ser_data["permit_type"] = DecosPermitSerializer.PERMIT_VV
                        else:
                            ser_data[
                                "permit_type"
                            ] = DecosPermitSerializer.PERMIT_UNKNOWN

                        permit_serializer = DecosPermitSerializer(data=ser_data)
                        if permit_serializer.is_valid():
                            permits.append(permit_serializer.data)
                        else:
                            p_data = permit_serializer.data
                            print(p_data)
                            logger.error("permit_data is not valid")

                    else:
                        raw_data = folder["fields"]
                        ser_errors = serializer.errors
                        print(raw_data, ser_errors)
                        logger.error("serializer is not valid")
        return permits
