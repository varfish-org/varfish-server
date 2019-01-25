from django import template

from ..models import BackgroundJob
from ..plugins import BackgroundJobsPluginPoint

register = template.Library()


@register.simple_tag
def get_details_backgroundjobs(project):
    """Return active background jobs for the project details page"""
    return BackgroundJob.objects.filter(project=project).order_by("-pk")[:5]


#: Global map from job specialization name to model class.
JOB_SPECS = {}

# Setup the global map.
for plugin in BackgroundJobsPluginPoint.get_plugins():
    assert not (set(plugin.job_specs) & set(JOB_SPECS)), "Registering model twice!"
    JOB_SPECS.update(plugin.job_specs)


@register.filter
def specialize_job(bg_job):
    """Given a ``BackgroundJob``, return the specialized job if any.

    Specialized job models are linked back to the ``BackgroundJob`` through a ``OneToOneField`` named ``bg_job``.
    """
    klass = JOB_SPECS.get(bg_job.job_type)
    if not klass:
        return bg_job
    else:
        return klass.objects.get(bg_job=bg_job)
