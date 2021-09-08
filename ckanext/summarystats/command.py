# -*- coding: utf-8 -*-
import logging
import ckan.model as model
import ckan.plugins.toolkit as toolkit

from .implementations import is_eligible
from .package_helper import package_helper
from .jobs import stats_job

log = logging.getLogger(__name__)


class SummaryStatsCmd:
    def __init__(self, fg):
        self.run_in_foreground = fg
        self.helper = package_helper()

    def identify_pkg(self, id):
        # try with id
        package = toolkit.get_action("package_show")({"ignore_auth": True}, {"id": id})
        # try with name
        if not package:
            package = toolkit.get_action("package_show")(
                {"ignore_auth": True}, {"name": id}
            )
        if not package:
            log.info("No package found by id or name for input " + id)
            return False
        else:
            return package

    def submit_all_pkgs(self):
        package_list = toolkit.get_action("package_search")(
            {"model": model, "ignore_auth": True},
            {"include_private": True, "rows": 1000},
        )
        for pkg in package_list.get("results", []):
            self.resubmit_pkg(pkg)

    def resubmit_pkg(self, package):

        dataset_id = package.get("id")
        if is_eligible(package):
            self.helper.add_message(dataset_id)
            if self.run_in_foreground:
                log.info("Starting summary stats job")
                stats_job(dataset_id)
            else:
                log.info(
                    "Enqueueing summary stats job for dataset {} ({})".format(
                        dataset_id, package.get("name")
                    )
                )
                toolkit.enqueue_job(
                    stats_job,
                    [dataset_id],
                    rq_kwargs={"timeout": 21600},
                    queue=u"summarystats",
                )
        else:
            log.info(
                "Skipping summary stats job for ineligible dataset {} ({})".format(
                    dataset_id, package.get("name")
                )
            )
