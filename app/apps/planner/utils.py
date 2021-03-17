from geopy.distance import distance


def filter_out_cases(cases, stadia=[]):
    """
    Returns a list of cases without the given stadia
    """
    if len(stadia) == 0:
        return cases

    def has_stadium(case):
        return case["stadium"] not in stadia

    return list(filter(lambda case: has_stadium(case), cases))


def filter_cases(cases, stadia):
    """
    Returns a list of cases with the given stadia
    """
    if len(stadia) == 0:
        return cases

    def has_stadium(case):
        return case["stadium"] in stadia

    return list(filter(lambda case: has_stadium(case), cases))


def remove_cases_from_list(cases, cases_to_remove):
    """
    Returns a new list without the 'cases_to_remove' items
    """
    cases_to_remove = [case.get("case_id") for case in cases_to_remove]

    def should_not_remove(case):
        return case.get("case_id") not in cases_to_remove

    new_list = list(filter(lambda case: should_not_remove(case), cases))

    return new_list


def get_case_coordinates(cases):
    """
    Maps the cases to an array of coordinates
    """
    coordinates = list(
        map(lambda case: [case["address"]["lat"], case["address"]["lng"]], cases)
    )

    return coordinates


def calculate_geo_distances(center, cases):
    """
    Returns a set of distances in KM from the given center
    """
    case_coordinates = get_case_coordinates(cases)
    distances = [
        distance(center, coordinates).km * 1000 for coordinates in case_coordinates
    ]

    return distances


def filter_cases_with_missing_coordinates(cases):
    """
    Cases with polluted data (missing coordinates) are removed
    """

    def has_coordinates(case):
        address = case.get("address", {})
        return address.get("lat", None) and address.get("lng", None)

    return list(filter(lambda case: has_coordinates(case), cases))


def filter_cases_with_postal_code(cases, ranges=[]):
    """
    Returns a list of cases for which the postal code falls within the given start and end range
    """

    if not ranges:
        return cases

    def is_in_range(case, range):
        range_start = range.get("range_start")
        range_end = range.get("range_end")

        if range_start > range_end:
            raise ValueError("Start range can't be larger than end_range")

        postal_code = case.get("postal_code")
        postal_code_numbers = int(postal_code[:4])

        return range_start <= postal_code_numbers <= range_end

    def is_in_ranges(case, ranges):
        for range in ranges:
            if is_in_range(case, range):
                return True
        return False

    cases = filter(lambda case: is_in_ranges(case, ranges), cases)
    return list(cases)
