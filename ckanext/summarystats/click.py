# -*- coding: utf-8 -*-

import click
from ckanext.summarystats.command import SummaryStatsCmd


@click.group()
def summarystats():
    """summarystats commands

    Usage:

        summarystats submit <dataset-spec>

            Submit the given datasets' for summary statistics
            (They are added to the queue for CKAN's task worker.

            where <dataset-spec> is one of:

                <dataset-name> - Submit a particular dataset's resources

                <dataset-id> - Submit a particular dataset's resources

                all - Submit all datasets' resources to the DataStore
    """
    pass


@summarystats.command()
@click.argument(u"dataset-spec")
@click.option(
    "--fg",
    is_flag=True,
    default=False,
    help="Runs the summarystats job in the foreground",
)
def submit(dataset_spec, fg):
    """
    summarystats submit <dataset-spec>
    """
    cmd = SummaryStatsCmd(fg)
    if dataset_spec == "all":
        cmd.submit_all_pkgs()
    else:
        pkg_id = cmd.identify_pkg(dataset_spec)
        if pkg_id:
            cmd.resubmit_pkg(pkg_id)


def get_commands():
    return [summarystats]
