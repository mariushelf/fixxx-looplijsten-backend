from settings.const import EXCLUDE_STADIA
from utils.queries import prepare_bwv_case_for_zks
from utils.query_helpers import do_query


def get_eligible_stadia(starting_date, stages):
    """
    Gets stadia which are eligible for planning
    """

    # Due to a recent change in the process, a new stage was introduced which can be open during
    # other stages. This overrules open stages that are relevant for generating itineraries
    # exclude_stadia is now added to filter out this process.

    query = """
            SELECT
            sta_oms AS stadium,
            sta_nr AS sta_nr,
            stadia_id,
            peildatum,
            begindatum AS begindatum_stadium,
            einddatum AS einddatum_stadium
            FROM import_stadia
            WHERE einddatum is Null
            AND begindatum > %(starting_date)s
            AND peildatum < NOW()
            AND sta_oms IN %(stages)s
            AND sta_oms NOT IN %(exclude_stadia)s
            """

    args = {
        "starting_date": starting_date,
        "stages": tuple(stages),
        "exclude_stadia": EXCLUDE_STADIA,
    }
    stadia = do_query(query, args)

    # Parses the case_id from the stadia_id and maps it in dictionary to easily access the stadia
    stadia_dictionary = {}
    for stadium in stadia:
        stadia_id = stadium["stadia_id"]
        case_id_raw = stadia_id.split("_")
        case_id_raw.pop()
        case_id = "_".join(case_id_raw)
        stadia_dictionary[case_id] = stadium

    return stadia_dictionary


def get_eligible_cases(projects):
    """
    Gets cases which are eligible for planning
    """

    query = """
            SELECT
              DISTINCT zaak_id AS id,
              import_wvs.beh_oms AS case_reason,
              import_wvs.is_sia as is_sia,
              import_adres.postcode AS postal_code,
              import_adres.sttnaam AS street_name,
              import_adres.hsnr AS street_number,
              import_adres.hsltr AS suffix_letter,
              import_adres.toev AS suffix,
              import_adres.wzs_lon AS lng,
              import_adres.wzs_lat as lat
            FROM import_wvs
            INNER JOIN
              import_adres ON import_adres.adres_id = import_wvs.adres_id
            WHERE beh_oms IN %(projects)s
            AND afs_code is NULL
            """

    args = {"projects": tuple(projects)}
    cases = do_query(query, args)

    return [prepare_bwv_case_for_zks(c) for c in cases]


def match_cases_to_stages(cases, stages):
    """
    Returns a list of cases which have been matched to stages
    The result is a filtered list of cases which are still open and can be planned
    """
    filtered_cases = []

    for case in cases:
        case_id = case.get("id")
        stage = stages.get(case_id, None)

        if stage:
            filtered_cases.append({**case, **stage})

    return filtered_cases


def get_cases_from_bwv(starting_date, projects, stages):
    # Due to a flaw in the BWV database design, there is no direct relationship
    # between the stadia and the cases. That's why two queries and matching are needed
    eligible_cases = get_eligible_cases(projects)
    eligible_stages = get_eligible_stadia(starting_date, stages)
    matched_cases = match_cases_to_stages(eligible_cases, eligible_stages)

    return matched_cases
