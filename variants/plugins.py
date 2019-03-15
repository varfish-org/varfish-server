from projectroles.plugins import ProjectAppPluginPoint
from bgjobs.plugins import BackgroundJobsPluginPoint

from .models import (
    Case,
    SmallVariantComment,
    SmallVariantFlags,
    ExportFileBgJob,
    ExportProjectCasesFileBgJob,
    DistillerSubmissionBgJob,
    ComputeProjectVariantsStatsBgJob,
    FilterBgJob,
    ProjectCasesFilterBgJob,
    ClinvarBgJob,
)
from .urls import urlpatterns


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "variants"
    title = "Cases"
    urls = urlpatterns
    # ...

    icon = "hospital-o"

    entry_point_url_id = "variants:case-list"

    description = "Cases"

    #: Required permission for accessing the app
    app_permission = "variants.view_data"

    #: Enable or disable general search from project title bar
    search_enable = True

    #: List of search object types for the app
    search_types = ["case"]

    #: Search results template
    search_template = "variants/_search_results.html"

    #: App card template for the project details page
    details_template = "variants/_details_card.html"

    #: App card title for the project details page
    details_title = "VarFish App Overview"

    #: Position in plugin ordering
    plugin_ordering = 10

    def search(self, search_term, user, search_type=None, keywords=None):
        """
        Return app items based on a search term, user, optional type and
        optional keywords
        :param search_term: String
        :param user: User object for user initiating the search
        :param search_type: String
        :param keywords: List (optional)
        :return: Dict
        """
        items = []

        if not search_type:
            cases = Case.objects.find(search_term, keywords)
            items = list(cases)
            items.sort(key=lambda x: x.name.lower())
        elif search_type == "case":
            items = Case.objects.find(search_term, keywords).order_by("name")

        return {"all": {"title": "Cases", "search_types": ["case"], "items": items}}

    def get_extra_data_link(self, extra_data, name):
        """Return link for the given label that started with ``"extra-"``."""
        if name == "extra-flag_values":
            return extra_data["flag_values"]
        else:
            return "(unknown %s)" % name

    def get_object_link(self, model_str, uuid):
        """
        Return URL for referring to a object used by the app, along with a
        label to be shown to the user for linking.
        :param model_str: Object class (string)
        :param uuid: sodar_uuid of the referred object
        :return: Dict or None if not found
        """
        obj = self.get_object(eval(model_str), uuid)

        if isinstance(obj, SmallVariantComment):
            return {"url": obj.get_absolute_url(), "label": obj.shortened_text()}
        elif isinstance(obj, SmallVariantFlags):
            return {"url": obj.get_absolute_url(), "label": obj.human_readable()}
        elif isinstance(obj, Case):
            return {"url": obj.get_absolute_url(), "label": obj.name}

        return None


class BackgroundJobsPlugin(BackgroundJobsPluginPoint):
    """Plugin for registering background jobs with ``bgjobs`` app."""

    #: Slug used in URLs and similar places.
    name = "variants"
    #: Human-readable title.
    title = "Variants Background Jobs"

    #: Return name-to-class mapping for background job class specializations.
    job_specs = {
        ExportFileBgJob.spec_name: ExportFileBgJob,
        DistillerSubmissionBgJob.spec_name: DistillerSubmissionBgJob,
        ComputeProjectVariantsStatsBgJob.spec_name: ComputeProjectVariantsStatsBgJob,
        ExportProjectCasesFileBgJob.spec_name: ExportProjectCasesFileBgJob,
        FilterBgJob.spec_name: FilterBgJob,
        ProjectCasesFilterBgJob.spec_name: ProjectCasesFilterBgJob,
        ClinvarBgJob.spec_name: ClinvarBgJob,
    }
