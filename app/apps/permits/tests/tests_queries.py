import json
from datetime import datetime
from unittest.mock import Mock, patch

from apps.permits.api_queries_decos_join import DecosJoinConf, VakantieverhuurMeldingen
from apps.permits.serializers import VakantieverhuurRentalInformationSerializer
from django.test import TestCase


class DecosJoinConfTest(TestCase):
    MOCK_CONF = (
        (
            "78F23C45E0FD43B19FF98633FE11C7D3",
            "B_EN_B_VERGUNNING",
        ),
        (
            "91D81A4BF70147D880A40A3D4FEA8F14",
            "VAKANTIEVERHUURVERGUNNING",
        ),
        (
            "6D7A9C0DB6584E4DB149F49A568F37EF",
            "OMZETTINGSVERGUNNING",
        ),
        (
            "02C281346BE44AC59E55C6212D0EE063",
            "SPLITTINGSVERGUNNING",
        ),
        (
            "EEB05166A55F47AC9393646AD7CA02DD",
            "ONTREKKING_VORMING_SAMENVOEGING_VERGUNNINGEN",
        ),
        (
            "27FB47C0444341828598F2AB546B618C",
            "LIGPLAATSVERGUNNING",
        ),
    )
    MOCK_EXPRESSION = "{date6} <= {ts_now} and {date7} >= {ts_now} and '{dfunction}'.startswith('Verleend')"
    MOCK_INITIAL_DATA = {
        "date5": 9999999999,
        "date6": 9999999999,
        "date7": 1,
        "dfunction": "Niet verleend",
    }
    MOCK_FIELD_MAPPING = {
        "date6": "DATE_FROM",
        "date7": "DATE_UNTIL",
        "dfunction": "RESULT_VERBOSE",
        "text45": "PERMIT_NAME",
    }

    def test_add_conf(self):
        """
        Can add conf
        """

        conf_instance = DecosJoinConf()

        self.assertEqual(len(conf_instance), 0)

        conf_instance.add_conf(self.MOCK_CONF)

        self.assertEqual(len(conf_instance), len(self.MOCK_CONF))

    def test_add_multiple_conf(self):
        """
        Can add multiple conf
        """

        conf_instance = DecosJoinConf()

        self.assertEqual(len(conf_instance), 0)

        conf_instance.add_conf(self.MOCK_CONF)
        conf_instance.add_conf(self.MOCK_CONF)

        self.assertEqual(len(conf_instance), len(self.MOCK_CONF))

    def test_get_book_keys(self):
        """
        Can add get book keys
        """

        conf_instance = DecosJoinConf()

        conf_instance.add_conf(self.MOCK_CONF)

        self.assertEqual(conf_instance.get_book_keys(), [v[0] for v in self.MOCK_CONF])

    def test_get_conf_by_book_key(self):
        """
        Can add get conf by book key
        """

        MOCK_BOOK_KEY_CONF = {
            DecosJoinConf.DECOS_JOIN_BOOK_KEY: self.MOCK_CONF[0][0],
            DecosJoinConf.PERMIT_TYPE: self.MOCK_CONF[0][1],
            DecosJoinConf.EXPRESSION_STRING: self.MOCK_EXPRESSION,
            DecosJoinConf.INITIAL_DATA: self.MOCK_INITIAL_DATA,
            DecosJoinConf.FIELD_MAPPING: self.MOCK_FIELD_MAPPING,
        }
        conf_instance = DecosJoinConf()

        conf_instance.set_default_expression(self.MOCK_EXPRESSION)
        conf_instance.set_default_initial_data(self.MOCK_INITIAL_DATA)
        conf_instance.set_default_field_mapping(self.MOCK_FIELD_MAPPING)
        conf_instance.add_conf(self.MOCK_CONF)

        self.assertEqual(
            conf_instance.get_conf_by_book_key(self.MOCK_CONF[0][0]), MOCK_BOOK_KEY_CONF
        )

    def test_map_data_on_conf_keys(self):
        """
        Can map data on conf keys
        """

        MOCK_DATA = {
            "date6": "date6_value",
            "date7": "date7_value",
            "dfunction": "dfunction_value",
            "text4": "text4_value",
        }

        conf_instance = DecosJoinConf()

        conf_instance.set_default_expression(self.MOCK_EXPRESSION)
        conf_instance.set_default_initial_data(self.MOCK_INITIAL_DATA)
        conf_instance.set_default_field_mapping(self.MOCK_FIELD_MAPPING)
        conf_instance.add_conf(self.MOCK_CONF)
        conf = conf_instance.get_conf_by_book_key(self.MOCK_CONF[0][0])

        self.assertEqual(
            conf_instance.map_data_on_conf_keys(MOCK_DATA, conf),
            {
                "DATE_FROM": "date6_value",
                "DATE_UNTIL": "date7_value",
                "RESULT_VERBOSE": "dfunction_value",
            },
        )

    def test_datestring_to_timestamp(self):
        """
        Can convert datestring to timestamp
        """

        MOCK_DATESTRING = "2020-08-26T11:59:35"
        MOCK_NO_DATESTRING = "mbk2020-08-26T11::59:35:98"

        self.assertEqual(
            DecosJoinConf().datestring_to_timestamp(MOCK_DATESTRING), 1598400000.0
        )
        self.assertEqual(
            DecosJoinConf().datestring_to_timestamp(MOCK_NO_DATESTRING),
            MOCK_NO_DATESTRING,
        )

    def test_clean_data(self):
        """
        Can clean_data
        """

        MOCK_DATESTRING = "2020-08-26T11:59:35"
        MOCK_NO_DATESTRING = "mbk2020-08-26T11::59:35:98"

        MOCK_DATA = {
            "field_datestring": MOCK_DATESTRING,
            "field_no_datestring": MOCK_NO_DATESTRING,
        }

        self.assertEqual(
            DecosJoinConf().clean_data(MOCK_DATA),
            {
                "field_datestring": 1598400000.0,
                "field_no_datestring": MOCK_NO_DATESTRING,
            },
        )

    def test_expression_no_data(self):
        """
        Test fail when trying to validate data without data
        """

        MOCK_CONF_BOOK_KEY = "1234567"
        MOCK_CONF_TYPE = "my_conf"
        MOCK_CONF_EXPRESSION = "{date6} == {ts_now}"

        MOCK_CONF = (
            (
                MOCK_CONF_BOOK_KEY,
                MOCK_CONF_TYPE,
                MOCK_CONF_EXPRESSION,
            ),
        )

        conf_instance = DecosJoinConf()

        conf_instance.add_conf(MOCK_CONF)

        conf = conf_instance.get_conf_by_book_key(MOCK_CONF_BOOK_KEY)

        dt = datetime.strptime("2020-08-26", "%Y-%m-%d")

        self.assertEqual(conf_instance.expression_is_valid(None, conf, dt), False)

    def test_expression_no_datetime(self):
        """
        Test fail when trying to validate data without datetime
        """

        MOCK_CONF_BOOK_KEY = "1234567"
        MOCK_CONF_TYPE = "my_conf"
        MOCK_CONF_EXPRESSION = "{date6} == {ts_now}"

        MOCK_CONF = (
            (
                MOCK_CONF_BOOK_KEY,
                MOCK_CONF_TYPE,
                MOCK_CONF_EXPRESSION,
            ),
        )

        conf_instance = DecosJoinConf()

        conf_instance.add_conf(MOCK_CONF)

        conf = conf_instance.get_conf_by_book_key(MOCK_CONF_BOOK_KEY)

        self.assertEqual(conf_instance.expression_is_valid(None, conf, None), False)

    def test_expression_no_conf(self):
        """
        Test fail when trying to validate data without conf
        """

        MOCK_CONF_BOOK_KEY = "1234567"

        MOCK_DATA = {
            "date66": "2020-08-26T11:59:35",
            "date7": "date7_value",
            "dfunction": "dfunction_value",
            "text4": "text4_value",
        }

        conf_instance = DecosJoinConf()

        conf = conf_instance.get_conf_by_book_key(MOCK_CONF_BOOK_KEY)

        dt = datetime.strptime("2020-08-26", "%Y-%m-%d")

        self.assertEqual(conf_instance.expression_is_valid(MOCK_DATA, conf, dt), False)

    def test_expression_missing_field_name(self):
        """
        Test fail when trying to validate data when fields are missing
        """

        MOCK_CONF_BOOK_KEY = "1234567"
        MOCK_CONF_TYPE = "my_conf"
        MOCK_CONF_EXPRESSION = "{date6} == {ts_now}"

        MOCK_DATA = {
            "date66": "2020-08-26T11:59:35",
            "date7": "date7_value",
            "dfunction": "dfunction_value",
            "text4": "text4_value",
        }

        MOCK_CONF = (
            (
                MOCK_CONF_BOOK_KEY,
                MOCK_CONF_TYPE,
                MOCK_CONF_EXPRESSION,
            ),
        )

        conf_instance = DecosJoinConf()

        conf_instance.add_conf(MOCK_CONF)

        conf = conf_instance.get_conf_by_book_key(MOCK_CONF_BOOK_KEY)

        dt = datetime.strptime("2020-08-26", "%Y-%m-%d")

        self.assertEqual(conf_instance.expression_is_valid(MOCK_DATA, conf, dt), False)

    def test_expression_missing_field_name_with_initial_data(self):
        """
        Test succeeded when trying to validate data when fields are missing but initial data is provided
        """

        MOCK_CONF_BOOK_KEY = "1234567"
        MOCK_CONF_TYPE = "my_conf"
        MOCK_CONF_EXPRESSION = "{date6} == {ts_now}"

        MOCK_DATA = {
            "date66": "2020-08-26T11:59:35",
            "date7": "date7_value",
            "dfunction": "dfunction_value",
            "text4": "text4_value",
        }

        MOCK_CONF = (
            (
                MOCK_CONF_BOOK_KEY,
                MOCK_CONF_TYPE,
                MOCK_CONF_EXPRESSION,
            ),
        )

        conf_instance = DecosJoinConf()

        conf_instance.set_default_initial_data({"date6": 1598400000.0})
        conf_instance.add_conf(MOCK_CONF)

        conf = conf_instance.get_conf_by_book_key(MOCK_CONF_BOOK_KEY)

        dt = datetime.strptime("2020-08-26", "%Y-%m-%d")

        self.assertEqual(conf_instance.expression_is_valid(MOCK_DATA, conf, dt), True)

    def test_expression_is_valid(self):
        """
        Test succeeded when trying to validate data
        """

        MOCK_CONF_BOOK_KEY = "1234567"
        MOCK_CONF_TYPE = "my_conf"
        MOCK_CONF_EXPRESSION = "{date6} >= {ts_now}"

        MOCK_DATA = {
            "date6": "2020-08-26T11:59:35",
            "date7": "date7_value",
            "dfunction": "dfunction_value",
            "text4": "text4_value",
        }

        MOCK_CONF = (
            (
                MOCK_CONF_BOOK_KEY,
                MOCK_CONF_TYPE,
                MOCK_CONF_EXPRESSION,
            ),
        )

        conf_instance = DecosJoinConf()

        conf_instance.add_conf(MOCK_CONF)

        conf = conf_instance.get_conf_by_book_key(MOCK_CONF_BOOK_KEY)
        dt = datetime.strptime("2020-08-26", "%Y-%m-%d")

        self.assertEqual(conf_instance.expression_is_valid(MOCK_DATA, conf, dt), True)

    def test_expression_is_not_valid(self):
        """
        Test failed when trying to validate data
        """

        MOCK_CONF_BOOK_KEY = "1234567"
        MOCK_CONF_TYPE = "my_conf"
        MOCK_CONF_EXPRESSION = "{date6} < {ts_now}"

        MOCK_DATA = {
            "date6": "2020-08-26T11:59:35",
            "date7": "date7_value",
            "dfunction": "dfunction_value",
            "text4": "text4_value",
        }

        MOCK_CONF = (
            (
                MOCK_CONF_BOOK_KEY,
                MOCK_CONF_TYPE,
                MOCK_CONF_EXPRESSION,
            ),
        )

        conf_instance = DecosJoinConf()
        conf_instance.add_conf(MOCK_CONF)

        conf = conf_instance.get_conf_by_book_key(MOCK_CONF_BOOK_KEY)
        dt = datetime.strptime("2020-08-26", "%Y-%m-%d")

        self.assertEqual(conf_instance.expression_is_valid(MOCK_DATA, conf, dt), False)


class VakantieverhuurMeldingenTest(TestCase):
    def test_add_valid_data_1(self):
        """
        Test succeeds when trying to validate data
        """

        MOCK_DATA = [
            {
                "date1": "2020-07-26T00:00:00",
                "date6": "2020-07-26T00:00:00",
                "date7": "2020-07-29T00:00:00",
                "sequence": 2.0,
                "is_afmelding": True,
            },
            {
                "date1": "2020-07-26T00:00:00",
                "date6": "2020-07-26T00:00:00",
                "date7": "2020-07-29T00:00:00",
                "sequence": 1.0,
                "is_afmelding": False,
            },
        ]
        vakantieverhuur_meldingen = VakantieverhuurMeldingen()

        succeeded = vakantieverhuur_meldingen.add_data(MOCK_DATA)

        serializer = VakantieverhuurRentalInformationSerializer(
            data=vakantieverhuur_meldingen.get_set_by_year(
                2020, datetime.strptime("2020-07-28", "%Y-%m-%d")
            )
        )
        expected_result = '{"rented_days_count": 2, "planned_days_count": 0, "is_rented_today": true, "meldingen": [{"is_afmelding": true, "melding_date": "2020-07-26T00:00:00+0000", "first_day": "2020-07-27T00:00:00+0000", "last_day": "2020-07-28T00:00:00+0000"}, {"is_afmelding": false, "melding_date": "2020-07-26T00:00:00+0000", "first_day": "2020-07-27T00:00:00+0000", "last_day": "2020-07-28T00:00:00+0000"}]}'

        self.assertEqual(succeeded, True)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(json.dumps(serializer.data), expected_result)

    def test_add_valid_data_2(self):
        """
        Test succeeds when trying to validate data
        """

        MOCK_DATA = [
            {
                "date1": "2020-07-26T00:00:00",
                "date6": "2020-07-26T00:00:00",
                "date7": "2020-07-29T00:00:00",
                "sequence": 2.0,
                "is_afmelding": True,
            },
            {
                "date1": "2020-07-26T00:00:00",
                "date6": "2020-07-26T00:00:00",
                "date7": "2020-07-29T00:00:00",
                "sequence": 1.0,
                "is_afmelding": False,
            },
            {
                "date1": "2020-07-27T00:00:00",
                "date6": "2020-07-27T00:00:00",
                "date7": "2020-07-30T00:00:00",
                "sequence": 3.0,
                "is_afmelding": False,
            },
            {
                "date1": "2019-12-29T00:00:00",
                "date6": "2019-12-29T00:00:00",
                "date7": "2020-01-02T00:00:00",
                "sequence": 4.0,
                "is_afmelding": False,
            },
        ]
        vakantieverhuur_meldingen = VakantieverhuurMeldingen()

        succeeded = vakantieverhuur_meldingen.add_data(MOCK_DATA)

        serializer = VakantieverhuurRentalInformationSerializer(
            data=vakantieverhuur_meldingen.get_set_by_year(
                2020, datetime.strptime("2020-07-28", "%Y-%m-%d")
            )
        )
        expected_result = '{"rented_days_count": 3, "planned_days_count": 1, "is_rented_today": true, "meldingen": [{"is_afmelding": false, "melding_date": "2019-12-29T00:00:00+0000", "first_day": "2019-12-30T00:00:00+0000", "last_day": "2020-01-01T00:00:00+0000"}, {"is_afmelding": false, "melding_date": "2020-07-27T00:00:00+0000", "first_day": "2020-07-28T00:00:00+0000", "last_day": "2020-07-29T00:00:00+0000"}, {"is_afmelding": true, "melding_date": "2020-07-26T00:00:00+0000", "first_day": "2020-07-27T00:00:00+0000", "last_day": "2020-07-28T00:00:00+0000"}, {"is_afmelding": false, "melding_date": "2020-07-26T00:00:00+0000", "first_day": "2020-07-27T00:00:00+0000", "last_day": "2020-07-28T00:00:00+0000"}]}'

        self.assertEqual(succeeded, True)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(json.dumps(serializer.data), expected_result)


class DecosJoinRequestTest(TestCase):

    MOCK_DECOS_JOIN_VAKANTIEVERHUUR_MELDINGEN_ID = "E6325A942DF440B386D8DFFEC013F795"
    MOCK_DECOS_JOIN_VAKANTIEVERHUUR_AFMELDINGEN_ID = "F86015A1A927451082A9E2F2023EF8F7"

    @patch(
        "apps.permits.api_queries_decos_join.settings.DECOS_JOIN_DEFAULT_PERMIT_VALID_CONF"
    )
    @patch(
        "apps.permits.api_queries_decos_join.settings.DECOS_JOIN_VAKANTIEVERHUUR_MELDINGEN_ID"
    )
    @patch(
        "apps.permits.api_queries_decos_join.settings.DECOS_JOIN_VAKANTIEVERHUUR_AFMELDINGEN_ID"
    )
    def test_expression_is_not_valid(
        self, mock_afmelding_id, mock_melding_id, mock_conf
    ):
        """
        Test failed when trying to validate data
        """

        mock_conf.return_value = (("1234", "conf_name"),)
        mock_melding_id.return_value = self.MOCK_DECOS_JOIN_VAKANTIEVERHUUR_MELDINGEN_ID
        mock_afmelding_id.return_value = (
            self.MOCK_DECOS_JOIN_VAKANTIEVERHUUR_AFMELDINGEN_ID
        )

        self.assertEqual(
            mock_afmelding_id(), self.MOCK_DECOS_JOIN_VAKANTIEVERHUUR_AFMELDINGEN_ID
        )
