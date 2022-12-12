from ckan.plugins.interfaces import Interface
import pandas as pd


class ISummaryStats(Interface):
    """
    Interface to define custom summarystats usage
    """

    def is_eligible_for_summarystats(self, dataset):
        """
        Returns a boolean that is used to determine if summary stats should be
        calculated for the given dataset.
        """
        return False

    def calculate_summarystats(self, dataset):
        """
        Calculates summary statistics for a given dataset and returns a pandas
        data frame
        """
        return pd.DataFrame(["Dummy", "List"])
