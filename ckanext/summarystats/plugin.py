import ckan.plugins as plugins

from .jobs import enqueue_stats_job
from .click import get_commands


class SummarystatsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IResourceController, inherit=True)

    #######################################################################
    # IClick                                                              #
    # Command-line interface for submitting dataset processing jobs       #
    #######################################################################
    def get_commands(self):
        return get_commands()

    #######################################################################
    # IResourceController                                                 #
    # Hooks into a dataset's resource lifecycle                           #
    #######################################################################
    def after_create(self, context, resource):
        enqueue_stats_job(resource)

    # Runs before a resource has been updated
    def before_update(self, context, current, resource):
        context["file_uploaded"] = False
        if resource.get("upload", False):
            context["file_uploaded"] = True

    # Runs after a resource has been updated
    def after_update(self, context, resource):
        if context["file_uploaded"]:
            enqueue_stats_job(resource)
