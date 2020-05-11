"""
Tests for the health views
"""
from django.test import TestCase

from api.cases.const import ISSUEMELDING, TWEEDE_CONTROLE, ONDERZOEK_BUITENDIENST
from api.planner.utils import filter_cases
from api.planner.utils import filter_cases_with_missing_coordinates, filter_out_cases
from api.planner.utils import remove_cases_from_list, get_case_coordinates, filter_cases_with_postal_code


class UtilsTests(TestCase):
    def test_filter_cases(self):
        case_a = {'stadium': ONDERZOEK_BUITENDIENST}
        case_b = {'stadium': ISSUEMELDING}
        case_c = {'stadium': TWEEDE_CONTROLE}

        cases = [case_a, case_b, case_c]
        result = filter_cases(cases, [ONDERZOEK_BUITENDIENST, ISSUEMELDING])
        expected = [case_a, case_b]

        self.assertEquals(result, expected)

    def test_filter_cases_empty(self):
        result = filter_cases([], [ONDERZOEK_BUITENDIENST, ISSUEMELDING])
        self.assertEquals(result, [])

    def test_filter_cases_no_stadia(self):
        case_a = {'stadium': ONDERZOEK_BUITENDIENST}
        case_b = {'stadium': ISSUEMELDING}
        case_c = {'stadium': TWEEDE_CONTROLE}

        cases = [case_a, case_b, case_c]
        result = filter_cases(cases, [])

        self.assertEquals(result, cases)

    def test_filter_cases_one_stadium(self):
        case_a = {'stadium': ONDERZOEK_BUITENDIENST}
        case_b = {'stadium': ISSUEMELDING}
        case_c = {'stadium': TWEEDE_CONTROLE}

        cases = [case_a, case_b, case_c]
        result = filter_cases(cases, [TWEEDE_CONTROLE])
        expected = [case_c]

        self.assertEquals(result, expected)

    def test_remove_cases_from_list(self):
        case_a = {'stadium': ONDERZOEK_BUITENDIENST, 'case_id': 'foo-a'}
        case_b = {'stadium': ISSUEMELDING, 'case_id': 'foo-b'}
        case_c = {'stadium': TWEEDE_CONTROLE, 'case_id': 'foo-c'}
        case_d = {'stadium': ONDERZOEK_BUITENDIENST, 'case_id': 'foo-d'}
        case_e = {'stadium': ISSUEMELDING, 'case_id': 'foo-e'}

        cases = [case_a, case_b, case_c, case_d, case_e]
        cases_to_remove = [case_b, case_e]

        result = remove_cases_from_list(cases, cases_to_remove)
        expected = [case_a, case_c, case_d]

        self.assertEquals(result, expected)

    def test_remove_cases_from_list_safety_fallback(self):
        '''
        Wil still succeed if tiems from the cases_to_remove don't exist in the cases list
        '''
        case_a = {'stadium': ONDERZOEK_BUITENDIENST, 'case_id': 'foo-a'}
        case_b = {'stadium': ISSUEMELDING, 'case_id': 'foo-b'}
        case_c = {'stadium': TWEEDE_CONTROLE, 'case_id': 'foo-c'}
        case_d = {'stadium': ONDERZOEK_BUITENDIENST, 'case_id': 'foo-d'}
        case_e = {'stadium': ISSUEMELDING, 'case_id': 'foo-e'}
        case_not_in_list = {'stadium': ISSUEMELDING, 'case_id': 'foo-f'}

        cases = [case_a, case_b, case_c, case_d, case_e]
        cases_to_remove = [case_a, case_b, case_not_in_list]

        result = remove_cases_from_list(cases, cases_to_remove)
        expected = [case_c, case_d, case_e]

        self.assertEquals(result, expected)

    def test_get_case_coordinates(self):
        case_a = {'lat': 0, 'lng': 1, 'stadium': ONDERZOEK_BUITENDIENST, 'case_id': 'foo-a'}
        case_b = {'lat': 2, 'lng': 3, 'stadium': ISSUEMELDING, 'case_id': 'foo-b'}
        case_c = {'lat': 4, 'lng': 5, 'stadium': TWEEDE_CONTROLE, 'case_id': 'foo-c'}
        cases = [case_a, case_b, case_c]
        case_coordinates = get_case_coordinates(cases)
        expected = [[0, 1], [2, 3], [4, 5]]

        self.assertEquals(case_coordinates, expected)

    def test_filter_cases_with_missing_coordinates(self):
        '''
        Should filter out cases with missing coordinates
        '''
        valid_case = {'stadium': ISSUEMELDING, 'lat': 12, 'lng': -69}
        cases = [
            {'stadium': ONDERZOEK_BUITENDIENST},
            {'stadium': ISSUEMELDING, 'lat': 12},
            {'stadium': ONDERZOEK_BUITENDIENST, 'lng': -69},
            {'stadium': ISSUEMELDING, 'lat': 12},
            {'stadium': ISSUEMELDING, 'lat': None, 'lng': -69},
            {'stadium': ONDERZOEK_BUITENDIENST, 'lat': 12, 'lng': None},
            {'stadium': ONDERZOEK_BUITENDIENST, 'lat': None, 'lng': None},
            valid_case,
        ]

        filtered_cases = filter_cases_with_missing_coordinates(cases)
        self.assertEquals(filtered_cases, [valid_case])

    def test_filter_out_cases(self):
        case_a = {'stadium': ONDERZOEK_BUITENDIENST}
        case_b = {'stadium': ISSUEMELDING}
        case_c = {'stadium': TWEEDE_CONTROLE}

        cases = [case_a, case_b, case_c]
        result = filter_out_cases(cases, [ONDERZOEK_BUITENDIENST, ISSUEMELDING])
        expected = [case_c]

        self.assertEquals(result, expected)

    def test_filter_out_cases_empty(self):
        result = filter_out_cases([], [ONDERZOEK_BUITENDIENST, ISSUEMELDING])
        self.assertEquals(result, [])

    def test_filter_out_cases_no_stadia(self):
        case_a = {'stadium': ONDERZOEK_BUITENDIENST}
        case_b = {'stadium': ISSUEMELDING}
        case_c = {'stadium': TWEEDE_CONTROLE}

        cases = [case_a, case_b, case_c]
        result = filter_out_cases(cases, [])

        self.assertEquals(result, cases)

    def test_filter_out_cases_one_stadium(self):
        case_a = {'stadium': ONDERZOEK_BUITENDIENST}
        case_b = {'stadium': ISSUEMELDING}
        case_c = {'stadium': TWEEDE_CONTROLE}

        cases = [case_a, case_b, case_c]
        result = filter_out_cases(cases, [TWEEDE_CONTROLE])
        expected = [case_a, case_b]

        self.assertEquals(result, expected)

    def test_filter_cases_with_postal_code_empty_list(self):
        '''
        Should just return an empty list
        '''
        cases = filter_cases_with_postal_code([])
        self.assertEqual(cases, [])

    def test_filter_cases_with_postal_code_wrong_range(self):
        '''
        Should throw error if the start range is larger than end range
        '''
        FOO_START_RANGE = 2000
        FOO_END_RANGE = 1000

        with self.assertRaises(ValueError):
            filter_cases_with_postal_code([], FOO_START_RANGE, FOO_END_RANGE)

    def test_filter_cases_with_postal_code(self):
        '''
        Returns the cases which fall within the given range
        '''
        FOO_START_RANGE = 1000
        FOO_END_RANGE = 2000

        FOO_CASE_A = {'postal_code': '1055XX'}
        FOO_CASE_B = {'postal_code': '2055XX'}
        FOO_CASE_C = {'postal_code': '2000XX'}
        FOO_CASE_D = {'postal_code': '1000XX'}
        FOO_CASE_E = {'postal_code': '0000XX'}

        cases = [FOO_CASE_A, FOO_CASE_B, FOO_CASE_C, FOO_CASE_D, FOO_CASE_E]

        filtered_cases = filter_cases_with_postal_code(
            cases,
            FOO_START_RANGE,
            FOO_END_RANGE
        )

        self.assertEquals(filtered_cases, [FOO_CASE_A, FOO_CASE_C, FOO_CASE_D])
