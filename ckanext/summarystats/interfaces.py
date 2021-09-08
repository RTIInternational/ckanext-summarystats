from ckan.plugins.interfaces import Interface
import pandas as pd


class ISummaryStats(Interface):
    """
    Interface to define custom summarystats usage
    """

    def is_eligible(self, dataset):
        u"""
        Returns a boolean that is used to determine if summary stats should be
        calculated for the given dataset.
        """
        return False

    def calculate_stats(self, dataset):
        u"""
        Calculates summary statistics for a given dataset and returns a pandas
        data frame
        """
        return pd.DataFrame(["Dummy", "List"])
