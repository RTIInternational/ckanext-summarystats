# The directory that files are stored temporarily for CKAN to upload them; we delete after
TEMPDIR = "/tmp/"


class SumstatsCalcError(Exception):
    """
    For implementations of calculate_summarystats to use if the parser needs to throw an error to
    display to the user
    """

    pass
