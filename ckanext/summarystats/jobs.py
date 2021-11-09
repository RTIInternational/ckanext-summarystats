from datetime import date, datetime, timedelta
import logging
import traceback
import ckan.plugins.toolkit as toolkit
from ckan.lib.jobs import job_from_id
from .constants import TEMPDIR, SumstatsCalcError
from .package_helper import (
    DUPLICATE_MSG,
    GENERAL_ERROR_MSG,
    package_helper,
    SUMSTATS_RSRC_TITLE,
    site_user_context,
)
from .implementations import is_eligible, calculate_stats

log = logging.getLogger(__name__)
pkg = package_helper()

# If resource is eligible, add stats job to worker queue
def enqueue_stats_job(resource):
    # Don't run if an automatically generated file is our subject
    if resource.get("generated") is None:
        dataset_id = resource["package_id"]
        dataset = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": dataset_id}
        )
        job_id = "summarystats-{}".format(dataset_id)
        try:
            job_from_id(job_id)  # Check if identical job is already queued
        except KeyError:
            # Job does not exist; try to create it
            if is_eligible(dataset):
                pkg.add_message(dataset_id)
                toolkit.enqueue_job(
                    stats_job,
                    [dataset_id],
                    rq_kwargs={
                        "job_id": job_id,
                        "timeout": 21600,
                    },
                    queue=u"summarystats",
                )


def is_older_than(resource, seconds):
    # Returns True if a resource is older than X seconds
    now = datetime.now()
    last_modified = datetime.fromisoformat(resource.get("last_modified"))
    return now - last_modified > timedelta(seconds=seconds)


# Call summary_stats implementation, set the returned file as resource on the dataset
def stats_job(dataset_id):
    try:
        dataset = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": dataset_id}
        )
        stats_dataframe = calculate_stats(dataset)

        # Write stats to file
        today = date.today().isoformat()
        filename = "{}-summary-stats-{}.tsv".format(dataset.get("name"), today)
        stats_dataframe.to_csv(TEMPDIR + filename, sep="\t")

        # Check if a summarystats resource already exists
        # and delete it if it's older than 30 seconds
        existing_rsrc = pkg.get_sumstats_resource(dataset)
        if existing_rsrc:
            if is_older_than(existing_rsrc, seconds=30):
                old_id = existing_rsrc.get("id")
                log.info("Deleting old summarystats {}".format(old_id))
                toolkit.get_action("resource_delete")(
                    site_user_context(), {"id": old_id}
                )
            else:
                log.info("SKIPPING creating summarystats resource. It was just made.")
                return
        log.info("Uploading summarystats for dataset {}".format(dataset_id))
        pkg.add_file(filename, SUMSTATS_RSRC_TITLE, dataset_id)
    except SumstatsCalcError as e:
        pkg.add_error(dataset["id"], error_text=str(e), expected=True)
        raise
    except KeyError:
        log.error(traceback.format_exc())
        error_text = "calculated summary statistics due to an unrecognized column name"
        pkg.add_error(dataset["id"], err_code=GENERAL_ERROR_MSG, error_text=error_text)
    except NotImplementedError:
        log.error(traceback.format_exc())
        pkg.add_error(dataset["id"], err_code=DUPLICATE_MSG)
    except Exception:
        # log.error(traceback.format_exc())
        pkg.add_error(
            dataset["id"],
            err_code=GENERAL_ERROR_MSG,
            error_text="calculated summary statistics",
        )
        raise
    # Retrieving package again now that it has the newly added resource
    dataset = toolkit.get_action("package_show")(
        {"ignore_auth": True}, {"id": dataset_id}
    )
