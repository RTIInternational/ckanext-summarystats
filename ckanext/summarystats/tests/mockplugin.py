import ckan.plugins as p
from ckanext.summarystats.interfaces import ISummaryStats
import pandas as pd


class SummarystatsMockPlugin(p.SingletonPlugin):
    """
    This plugin is
    - made available as `summarystats_mock_plugin` by the entrypoints list in setup.py
    - included in the plugin list in test_plugin.py
    It demonstrates how to use the SummaryStats plugin.
    """

    p.implements(ISummaryStats)

    def is_eligible(self, dataset):
        return True

    def calculate_stats(self, dataset):
        return pd.DataFrame(["Dummy", "List"])

    # More methods to be added later
