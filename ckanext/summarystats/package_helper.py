# -*- coding: utf-8 -*-
import logging
import os

from ckan import model
from ckan.common import config
import ckan.plugins.toolkit as toolkit

from .constants import TEMPDIR

from werkzeug.datastructures import FileStorage

log = logging.getLogger(__name__)


# These are dataset schema dependencies; they are required to be present in the dataset schema if you want to use them
SUMMARY_STATS_ERROR = "summarystats_error"
SUMMARY_STATS_PROCESSING = "summarystats_processing"

PROCESSING_MSG = "The resources you have uploaded are currently being processed for summary statistics. Please refresh the page or check back soon to see them completed."
GENERAL_ERROR_MSG = "error"
DATA_FILE_MISSING_MSG = "data_file_missing_column"
DUPLICATE_MSG = "duplicate"

# Just a constant for blank string
BLANK = ""

# Not sure if all of these are still used
messages = {
    DATA_FILE_MISSING_MSG: "There was a problem generating summary statistics from the files you've uploaded. The following columns were NOT present in the data file: {error_text}",
    GENERAL_ERROR_MSG: "There was a problem generating {error_text} from the files you've specified. Please ensure that the data in these files are correct.",
    DUPLICATE_MSG: "There was a problem generating summary statistics from the files you've uploaded. Please make sure there are no duplicate rows in your data file.",
    "Usecols do not match columns, columns expected but not found": "There was a problem generating summary statistics from the files you've uploaded. The following columns were not present in the {file_type} file: {error_text}. Please make sure the {file_type} file is tab delimited and has the required columns.",
    "could not convert string to float": "There was a problem generating summary statistics from the files you've uploaded. In the {file_type} file, the following value cannot be converted to a numeric value: {error_text}.",
}

SUMSTATS_RSRC_TITLE = "Calculated Summary Statistics"


def site_user_context():
    user = toolkit.get_action("get_site_user")(
        {"model": model, "ignore_auth": True}, {}
    )
    return {"ignore_auth": True, "user": user["name"], "auth_user_obj": None}


class package_helper:
    def has_error_message(self, key):
        return key in messages

    def add_error(
        self, package_id, err_code=None, error_text=None, file_type=None, expected=False
    ):
        """
        For implementors, raise SumstatsCalcError(error_message) to have this function apply
        the error_message to the dataset.
        """
        package = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": package_id}
        )
        pkg_text = ""
        if err_code is not None:
            pkg_text = messages.get(err_code)
            if error_text:
                pkg_text = pkg_text.format(
                    error_text=str(error_text), file_type=file_type
                )
        else:
            pkg_text = error_text

        package[SUMMARY_STATS_ERROR] = pkg_text
        package[SUMMARY_STATS_PROCESSING] = BLANK
        toolkit.get_action("package_revise")(
            site_user_context(),
            {
                "match__id": package_id,
                "update": {
                    SUMMARY_STATS_ERROR: pkg_text,
                    SUMMARY_STATS_PROCESSING: BLANK,
                },
            },
        )
        if expected:
            log.info("User error: {}".format(pkg_text))
            return

    def add_message(self, package_id):
        package = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": package_id}
        )
        package[SUMMARY_STATS_PROCESSING] = PROCESSING_MSG
        package[SUMMARY_STATS_ERROR] = BLANK
        toolkit.get_action("package_revise")(
            site_user_context(),
            {
                "match__id": package_id,
                "update": {
                    SUMMARY_STATS_PROCESSING: PROCESSING_MSG,
                    SUMMARY_STATS_ERROR: BLANK,
                },
            },
        )

    def add_file(self, path, name, package_id):
        package = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": package_id}
        )
        with open(TEMPDIR + path, "rb") as file:
            statsfile = None
            rsc_id = None
            for resource in package["resources"]:
                if resource["name"] == path:
                    statsfile = resource
                    rsc_id = resource["id"]
                    break

            resource_metadata = {
                "name": SUMSTATS_RSRC_TITLE,
                "resource_file_type": SUMSTATS_RSRC_TITLE,
                "package_id": package["id"],
                "format": "tsv",
                "generated": True,
            }
            if statsfile:
                # action = "resource_update"
                resource_metadata["id"] = statsfile["id"]
                toolkit.get_action("package_revise")(
                    site_user_context(),
                    {
                        "match__id": package_id,
                        f"update__resources__{rsc_id}": resource_metadata,
                        f"update__resources__{rsc_id}__upload": FileStorage(file),
                    },
                )
            else:
                # action = "resource_create"
                toolkit.get_action("package_revise")(
                    site_user_context(),
                    {
                        "match__id": package_id,
                        "update__resources__extend": [resource_metadata],
                        "update__resources__-1__upload": FileStorage(file),
                    },
                )

            os.remove("/tmp/" + path)

            updatedPackage = toolkit.get_action("package_show")(
                {"ignore_auth": True}, {"id": package["id"]}
            )
            updatedPackage[SUMMARY_STATS_ERROR] = BLANK
            updatedPackage[SUMMARY_STATS_PROCESSING] = BLANK
            final = toolkit.get_action("package_revise")(
                site_user_context(),
                {
                    "match__id": package_id,
                    "update": {
                        SUMMARY_STATS_ERROR: BLANK,
                        SUMMARY_STATS_PROCESSING: BLANK,
                    },
                },
            )
            return final.get("package")

    def get_sumstats_resource(self, dataset):
        for resource in dataset.get("resources"):
            if resource["resource_file_type"] == SUMSTATS_RSRC_TITLE:
                return resource
        return None

    def get_resource_file_path(self, resource):
        id = resource.get("id")
        dir1 = id[0:3]
        dir2 = id[3:6]
        base = config.get("ckan.storage_path")
        return base + "/resources/" + dir1 + "/" + dir2 + "/" + id[6:]
