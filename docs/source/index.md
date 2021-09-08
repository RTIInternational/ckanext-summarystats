[ckanext-summarystats documentation master file]: <> (This is a comment, it will not be included)

# ckanext-summarystats


```{toctree}
---
maxdepth: 2
---

```

[GitHub](https://github.com/RTIInternational/ckanext-summarystats)

This CKAN extension allows plugins to create summary statistics for a dataset that meets certain criteria. These summary stats are then uploaded to the dataset.

**Example summarystats usage in a plugin**

```
from ckanext.summarystats.interfaces import ISummaryStats

class MyPlugin(plugins.SingletonPlugin):
    plugins.implements(ISummaryStats)

    def is_eligible(self, dataset):
        """
        Returns a boolean to determine if summary stats should be
        calculated for the given dataset
        """
        # Some criteria
        if dataset.get("data_type") == "math":
            return True

    def calculate_stats(self, dataset):
        """
        Calculates summary statistics for a given dataset and
        returns a pandas data frame
        """
        # Get resource to generate stats dataframe
        stats_df = None
        resource_filepath = None
        for resource in dataset.get("resources"):
            if resource.get("resource_type") == "math":
                resource_filepath = get_resource_file_path()
                resource_dataframe = pd.read_csv(resource_filepath)
                # Do some transform to create a new dataframe
                stats_df = resource_dataframe

        return stats_df
```

When a dataset's resource is created or updated, summarystats will call `is_eligible` to see if it should `calculate_stats`.

## What sort of summary stats might be calculated?

A simple example could be a dataset containing tabular data resources where each row is a person's favorite food. Using this plugin, you could implement a `is_eligible` function that checks if the dataset does indeed contain such data, then implement a `calculate_stats` function to summarize the data to determine the top 10 favorite foods in the dataset.
