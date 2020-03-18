from utils.query_helpers import do_query


def get_eligible_stadia(stages):
    '''
    Gets stadia which are eligible for planning
    '''

    query = """
            SELECT
            sta_oms AS stadium,
            sta_nr AS sta_nr,
            stadia_id,
            einddatum
            FROM import_stadia
            WHERE einddatum is Null
            AND peildatum < NOW()
            AND sta_oms IN %(stages)s
            """

    args = {'stages': tuple(stages)}
    stadia = do_query(query, args)

    # Parses the case_id from the stadia_id and maps it in dictionary to easily access the stadia
    stadia_dictionary = {}
    for stadium in stadia:
        stadia_id = stadium['stadia_id']
        case_id_raw = stadia_id.split('_')
        case_id_raw.pop()
        case_id = '_'.join(case_id_raw)
        stadia_dictionary[case_id] = stadium

    return stadia_dictionary

def get_eligible_cases(starting_date, projects):
    '''
    Gets cases which are eligible for planning
    '''

    query = """
            SELECT
              DISTINCT zaak_id AS case_id,
              import_wvs.beh_oms AS case_reason,
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
            WHERE begindatum > %(starting_date)s
            AND beh_oms IN %(projects)s
            AND afs_code is NULL
            """

    args = {
        'starting_date': starting_date,
        'projects': tuple(projects)
    }
    cases = do_query(query, args)

    return cases

def match_cases_to_stages(cases, stages):
    '''
    Returns a list of cases which have been matched to stages
    The result is a filtered list of cases which are still open and can be planned
    '''
    filtered_cases = []

    for case in cases:
        case_id = case.get('case_id')
        stage = stages.get(case_id, None)

        if stage:
            filtered_cases.append({**case, **stage})

    return filtered_cases

def get_cases(starting_date, projects, stages):
    # Due to a flaw in the BWV database design, there is no direct relationship
    # between the stadia and the cases. That's why two queries and matching are needed
    eligible_cases = get_eligible_cases(starting_date, projects)
    eligible_stages = get_eligible_stadia(stages)
    matched_cases = match_cases_to_stages(eligible_cases, eligible_stages)

    return matched_cases
