# -*- coding: utf-8 -*-
import logging
import os
import sys

from ckan import model
from ckan.common import config
import ckan.plugins.toolkit as toolkit

from .constants import TEMPDIR

from werkzeug.datastructures import FileStorage

log = logging.getLogger(__name__)
PROCESSING = "processing"
BLANK = ""

messages = {
    "unknown_phenotype_headers": "There was a problem generating summary statistics from the files you've uploaded. The following columns were NOT present in the phenotype file: {error_text}",
    "data_file_missing_column": "There was a problem generating summary statistics from the files you've uploaded. The following columns were NOT present in the data file: {error_text}",
    "unknown_data_headers": "There was a problem generating summary statistics from the files you've uploaded. The following IDs were present in the phenotype file, but not the data file: ",
    PROCESSING: "The resources you have uploaded are currently being processed for summary statistics and visualizations. Please refresh the page or check back soon to see them completed.",
    "error": "There was a problem generating {error_text} from the files you've specified. Please ensure that the data in these files are correct.",
    "multiple_types": "There was a problem generating summary statistics from the files you've uploaded. Make sure that your data file and metadata file are referencing the same data type.",
    "Usecols do not match columns, columns expected but not found": "There was a problem generating summary statistics from the files you've uploaded. The following columns were not present in the {file_type} file: {error_text}. Please make sure the {file_type} file is tab delimited and has the required columns.",
    "could not convert string to float": "There was a problem generating summary statistics from the files you've uploaded. In the {file_type} file, the following value cannot be converted to a numeric value: {error_text}.",
    "duplicate": "There was a problem generating summary statistics from the files you've uploaded. Please make sure there are no duplicate molecules in your data file.",
}

user = toolkit.get_action("get_site_user")({"model": model, "ignore_auth": True}, {})
CONTEXT = {"ignore_auth": True, "user": user["name"], "auth_user_obj": None}
SUMSTATS_RSRC_TITLE = "Calculated Summary Statistics"


class package_helper:
    def has_error_message(self, key):
        return key in messages

    def add_error(self, package_id, message, error_text=None, file_type=None):
        package = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": package_id}
        )
        pkg_text = messages.get(message)
        if error_text:
            pkg_text = pkg_text.format(error_text=str(error_text), file_type=file_type)
        package["summary_stats_error"] = pkg_text
        package[PROCESSING] = BLANK
        toolkit.get_action("package_update")(CONTEXT, package)
        sys.exit(1)

    def add_message(self, package_id):
        package = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": package_id}
        )
        package[PROCESSING] = messages.get(PROCESSING)
        package["summary_stats_error"] = BLANK
        toolkit.get_action("package_update")(CONTEXT, package)

    def add_file(self, path, name, package_id):
        package = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": package_id}
        )
        with open(TEMPDIR + path, "rb") as file:
            statsfile = None
            for resource in package["resources"]:
                if resource["name"] == path:
                    statsfile = resource
                    break

            resource_metadata = {
                "name": SUMSTATS_RSRC_TITLE,
                "resource_file_type": SUMSTATS_RSRC_TITLE,
                "package_id": package["id"],
                "upload": FileStorage(file),
                "format": "tsv",
                "generated": True,
            }
            if statsfile:
                action = "resource_update"
                resource_metadata["id"] = statsfile["id"]
            else:
                action = "resource_create"

            toolkit.get_action(action)(CONTEXT, resource_metadata)
            os.remove("/tmp/" + path)

            updatedPackage = toolkit.get_action("package_show")(
                {"ignore_auth": True}, {"id": package["id"]}
            )
            updatedPackage["summary_stats_error"] = BLANK
            updatedPackage[PROCESSING] = BLANK
            final = toolkit.get_action("package_update")(CONTEXT, updatedPackage)
            return final

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
