from utils.query_helpers import do_query


def get_bwv_tables():
    """
    Gets bwv tables and columns
    """

    query = """
            SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
            """

    args = {}
    return do_query(query, args)


def get_bwv_columns(table_name):
    """
    Gets bwv columns by table_name
    """

    query = """
            SELECT column_name FROM information_schema.columns WHERE table_name = %(table_name)s;
            """

    args = {"table_name": table_name}
    return do_query(query, args)


def get_bwv_personen():
    """
    Returns all bwv_personen records
    """
    query = """
            SELECT *
            FROM
              bwv_personen
            """

    args = {}
    query_results = do_query(query, args)

    return query_results


def get_bwv_personen_hist():
    """
    Returns all bwv_personen_hist records
    """
    query = """
            SELECT *
            FROM
              bwv_personen_hist
            """

    args = {}
    query_results = do_query(query, args)

    return query_results
