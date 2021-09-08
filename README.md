# ckanext-mecfs-summarystats

``` 
plugin.py -> jobs.py -> implementations.py

implementations.py

* is_eligible -> Bool
* calculate_stats -> String
```

A plugin that creates summary statistics for a dataset that meets certain criteria. this plugin is for the mapMECFS website, and relies on schema changes/templates published in the `ckanext-mecfs` extension. As such, this extension should only be used with that one, and included after it.

### Workflow

`plugin.py`
* When either a new resource is created or a resource is updated,
  * The resource is passed to `validate_files_and_generate_stats()`

`validate_and_generate.py`
* Check to see if the resource has the `generated` metadata flag set to False or nonexistent
* The resource is validated using the `is_eligible` method, which is defined by the plugin extending this one
* If the above conditions are true, a processing message is added to the parent package, and a job is sent to the [queue](https://python-rq.org) to run `generate_files`
* The package is sent to `summary_stats()`

`summary_stats.py`
* The package is sent to `parser.py`, which retrieves the data file and phenotype file from the filesystem, and formats/processes them into a combined pandas dataframe based on our required formatting documentation, and provides meaningful errors if any steps fail in that transformation.
* The combined dataframe is grouped by `Sample_Source` and `Phenotype`
* Mean, std and count are calculated for each row (row per molecule -> sample source)
* The dataframe is stacked and reordered to create a hierarchical layout of groups
* For each pair of Phenotypes in each row, Wilcoxon Ranksum is generated and both the stat and p-value are added to the dataframe
* the dataframe is saved to the `/tmp` directory as a csv file, and the file path is returned

`validate_and_generate.py`
* The csv created above is retrieved from the filesystem
* The csv is uploaded as a new resource to the package, with the `generated` flag set to true
* the processing text is removed from the package




    