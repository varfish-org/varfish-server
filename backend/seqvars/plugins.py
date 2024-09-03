from bgjobs.plugins import BackgroundJobsPluginPoint

from seqvars.models.base import SeqvarsQueryExecutionBackgroundJob


class BackgroundJobsPlugin(BackgroundJobsPluginPoint):
    """Plugin for registering background jobs with ``bgjobs`` app."""

    name = "seqvars"
    title = "Seqvars Background Jobs"

    job_specs = {
        SeqvarsQueryExecutionBackgroundJob.spec_name: SeqvarsQueryExecutionBackgroundJob,
    }

    def get_extra_data_link(self, _extra_data, _name):
        return None

    def get_object_link(self, *args, **kwargs):
        return None
