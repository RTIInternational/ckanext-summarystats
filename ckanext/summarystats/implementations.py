import ckan.plugins as p
from ckanext.summarystats.interfaces import ISummaryStats

"""
These methods are getters for the actual implementations in the consuming plugin.

Plugins should add their own function using the interface
`ckanext.summarystats.interfaces.ISummaryStats`
"""


def is_eligible(dataset):
    """
    Calls a function, `is_eligible(dataset) -> boolean`
    that is used to determine if summary stats should be calculated for the
    given dataset
    """

    eligibility_func = None
    for plugin in p.PluginImplementations(ISummaryStats):
        if hasattr(plugin, "is_eligible"):
            eligibility_func = plugin.is_eligible

    if eligibility_func is None:
        raise Exception("No plugin implementing ISummaryStats was found.")

    return eligibility_func(dataset)


def calculate_stats(dataset):
    """
    Calls a function, `calculate_stats(dataset) -> pandas.DataFrame`
    that calculates summary statistics for a given dataset and returns a pandas
    data frame
    """

    summary_stats_func = None
    for plugin in p.PluginImplementations(ISummaryStats):
        if hasattr(plugin, "calculate_stats"):
            summary_stats_func = plugin.calculate_stats

    if summary_stats_func is None:
        raise Exception("No plugin implementing ISummaryStats was found.")

    return summary_stats_func(dataset)
