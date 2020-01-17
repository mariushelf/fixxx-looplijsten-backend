from utils.helpers import get_days_in_range
from utils.query_helpers import do_query, return_first_or_empty

def get_search_results(postal_code, street_number, suffix):
    suffix = suffix.replace(' ', '')
    suffix_query = ''
    if suffix:
        suffix_query = "WHERE LOWER(suffix) LIKE LOWER('{}%')".format(suffix)

    query = """
            SELECT
              case_id
            FROM
              (
                SELECT
                  import_wvs.zaak_id AS case_id,
                COALESCE(hsltr, '') || COALESCE(toev, '') AS suffix
                FROM
                  import_wvs
                INNER JOIN
                  import_adres
                ON
                  import_wvs.adres_id = import_adres.adres_id
                AND
                  import_wvs.afs_code is NULL
                AND
                  LOWER(postcode) = LOWER('{}')
                AND
                  hsnr = '{}'
              )
            AS
              case_preselect
            {}
            """.format(postal_code, street_number, suffix_query)

    case_ids = do_query(query)
    case_ids = [case_id['case_id'] for case_id in case_ids]
    cases = [get_case(case_id) for case_id in case_ids]

    return cases

def get_related_case_ids(case_id):
    query = """
            SELECT DISTINCT ON (import_wvs.zaak_id)
              import_adres.adres_id,
              import_adres.wng_id
            FROM import_adres INNER JOIN import_stadia ON import_adres.adres_id = import_stadia.adres_id
            INNER JOIN import_wvs ON import_stadia.adres_id = import_wvs.adres_id
            AND zaak_id = '{}'
              """.format(case_id)

    executed_query = do_query(query)
    return return_first_or_empty(executed_query)

def get_related_cases(adres_id):
    query = """
            SELECT wvs_nr as case_number, zaak_id as case_id, beh_oms AS case_reason
            FROM import_wvs
            WHERE adres_id = '{}'
            AND afs_code is Null
            """.format(adres_id)
    executed_query = do_query(query)

    return executed_query

def get_toezichthouder_name(toezichthouder_code):
    if toezichthouder_code:
        query = """
          SELECT naam FROM bwv_medewerkers where code = '{}'
          """.format(toezichthouder_code)

        executed_query = do_query(query)
        item = return_first_or_empty(executed_query)

        return item.get('naam', None)

    return None


def get_bwv_hotline_bevinding(wng_id):
    query = """
            SELECT
              toez_hdr1_code,
              toez_hdr2_code,
              bevinding_datum,
              bevinding_tijd,
              hit,
              opmerking,
              volgnr_bevinding
            FROM bwv_hotline_bevinding WHERE wng_id = '{}'
            ORDER BY volgnr_bevinding ASC
            """.format(wng_id)

    results = do_query(query)

    # Adds the user's names to the result data
    for result in results:
        toez_hdr1_code = result.get('toez_hdr1_code', None)
        toez_hdr2_code = result.get('toez_hdr2_code', None)

        result['toez_hdr1_naam'] = get_toezichthouder_name(toez_hdr1_code)
        result['toez_hdr2_naam'] = get_toezichthouder_name(toez_hdr2_code)

    return results

def get_bwv_hotline_melding(wng_id):
    query = """
            SELECT
              melding_datum,
              melder_anoniem,
              melder_naam,
              melder_emailadres,
              melder_telnr,
              situatie_schets
            FROM bwv_hotline_melding WHERE wng_id = '{}'
            ORDER BY melding_datum ASC
            """.format(wng_id)

    return do_query(query)

def get_bwv_personen(adres_id):
    query = """
            SELECT
              naam,
              voorletters,
              geslacht,
              geboortedatum,
              bwv_personen_hist.vestigingsdatum_adres,
              bwv_personen_hist.overlijdensdatum
            FROM bwv_personen_hist
            INNER JOIN bwv_personen
              ON bwv_personen.id = bwv_personen_hist.pen_id
              AND ads_id = '{}'
              AND bwv_personen_hist.vertrekdatum_adres is Null
            ORDER BY vestigingsdatum_adres DESC
            """.format(adres_id)

    return do_query(query)

def get_import_adres(wng_id):
    query = """
            SELECT
              sttnaam,
              hsnr,
              hsltr,
              toev,
              postcode,
              sbw_omschr,
              kmrs,
              landelijk_bag
            FROM import_adres WHERE wng_id = '{}'
            """.format(wng_id)

    executed_query = do_query(query)
    return return_first_or_empty(executed_query)

def get_import_stadia(case_id):
    query = """
            SELECT
              sta_oms,
              begindatum,
              einddatum,
              peildatum,
              sta_nr
            FROM
              import_stadia
            WHERE stadia_id LIKE '{}_%'
            ORDER BY sta_nr DESC
          """.format(case_id)

    return do_query(query)


def get_case(case_id):
    query = """
            SELECT
              import_wvs.zaak_id AS case_id,
              import_adres.postcode AS postal_code,
              import_adres.sttnaam AS street_name,
              import_adres.hsnr AS street_number,
              import_adres.hsltr AS suffix_letter,
              import_adres.toev AS suffix,
              import_stadia.sta_oms AS stadium,
              import_wvs.beh_oms AS case_reason
            FROM
              import_wvs
            INNER JOIN
              import_adres ON import_wvs.adres_id = import_adres.adres_id
            INNER JOIN
              import_stadia ON import_wvs.adres_id = import_stadia.adres_id
            AND
              stadia_id LIKE '{}_%'
            AND import_wvs.zaak_id = '{}'
            ORDER BY
              import_stadia.sta_nr DESC
            LIMIT 1
            """.format(case_id, case_id)

    executed_query = do_query(query)
    return return_first_or_empty(executed_query)

def get_open_cases(adres_id):
    # Note: Our current bwv dump doesn't export the complete history of cases ever
    # So this might not always be accurate (we'll have to check)
    query = """
            SELECT
              COUNT(adres_id) as num_open_cases
            FROM import_wvs
            WHERE adres_id='{}' AND afs_code is NULL
            """.format(adres_id)

    executed_query = do_query(query)
    return return_first_or_empty(executed_query)

def get_case_count(adres_id):
    query = """
              SELECT
                MAX(wvs_nr) as num_cases
              FROM import_wvs
              WHERE adres_id='{}'
            """.format(adres_id)

    executed_query = do_query(query)
    return return_first_or_empty(executed_query)

def get_case_basics(case_id):
    query = """
            SELECT
              wvs_nr as case_number,
              beh_oms as openings_reden
            FROM import_wvs WHERE zaak_id='{}'
            """.format(case_id)

    executed_query = do_query(query)
    return return_first_or_empty(executed_query)

def get_bwv_tmp(case_id, adres_id):
    case_count = get_case_count(adres_id)
    case_basics = get_case_basics(case_id)
    open_cases = get_open_cases(adres_id)
    return {**case_count, **case_basics, **open_cases}


def get_rented_days(notified_rentals):
    days = 0
    for notified_rental in notified_rentals:
        check_in = notified_rental['check_in']
        check_out = notified_rental['check_out']
        days += get_days_in_range(check_in, check_out)
    return days


def get_bwv_vakantieverhuur(wng_id):
    """
    Returns the current year's notified rentals
    """
    query = """
            SELECT
              datum_aanvang_verhuur as check_in,
              datum_einde_verhuur as check_out
            FROM
              bwv_vakantieverhuur
            WHERE
              date_part('year', datum_einde_verhuur) = date_part('year', CURRENT_DATE)
            AND
              wng_id = '{}'
            AND
              annuleer_date IS NULL
            ORDER BY check_in
            """.format(wng_id)

    query_results = do_query(query)
    get_rented_days(query_results)
    return query_results


def get_shortstay_license(wng_id):
    """
    Returns the shortstay license
    """

    query = """
            SELECT shortstay
            FROM bwv_woningen
            WHERE id='{}'
            """.format(wng_id)

    executed_query = do_query(query)
    return return_first_or_empty(executed_query)

def get_is_bnb_declared(wng_id):
    """
    Returns if the adress is currently declared as a bnb
    """

    query = """
            SELECT benb_melding as is_bnb_declared
            FROM bwv_woningen
            WHERE id='{}'
            """.format(wng_id)

    executed_query = do_query(query)
    return return_first_or_empty(executed_query)

def get_rental_information(wng_id):
    notified_rentals = get_bwv_vakantieverhuur(wng_id)
    rented_days = get_rented_days(notified_rentals)
    shortstay_license = get_shortstay_license(wng_id)
    is_bnb_declared = get_is_bnb_declared(wng_id)

    return {
        'notified_rentals': notified_rentals,
        'rented_days': rented_days,
        **shortstay_license,
        **is_bnb_declared
    }
