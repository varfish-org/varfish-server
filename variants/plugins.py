from django.core.urlresolvers import reverse

from projectroles.constants import get_sodar_constants
from projectroles.plugins import ProjectAppPluginPoint
from bgjobs.plugins import BackgroundJobsPluginPoint

from .models import (
    Case,
    CASE_STATUS_CHOICES,
    SmallVariantComment,
    SmallVariantFlags,
    ExportFileBgJob,
    ExportProjectCasesFileBgJob,
    DistillerSubmissionBgJob,
    ComputeProjectVariantsStatsBgJob,
    FilterBgJob,
    ProjectCasesFilterBgJob,
    SyncCaseListBgJob,
    ImportVariantsBgJob,
    CaseComments,
)
from .urls import urlpatterns
from .templatetags.variants_tags import case_status_to_color

# Global SODAR constants
SODAR_CONSTANTS = get_sodar_constants()


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
    details_title = "Cases Overview (top 5 most recently updated)"

    #: Position in plugin ordering
    plugin_ordering = 10

    #: The user settings for this app.
    app_settings = {
        "umd_predictor_api_token": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_USER"],
            "type": "STRING",  # STRING/INTEGER/BOOLEAN
            "default": "",
            "label": "UMD Predictor API Token",
            "placeholder": "paste your API token here",
            "description": (
                "In order to use the UMD score, you will need to create an account in the UMD Predictor site. "
                "Afterwards, you can obtain your token from your account settings page."
            ),
        },
        "latest_version_seen_changelog": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_USER"],
            "type": "STRING",
            "default": "",
            "label": "Changelog seen in version",
        },
        "user_defined_tags": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "STRING",
            "default": "",
            "label": "User defined tags to attach to cases",
            "description": (
                "Define tags to attach to a case. Deleted tags will stay attached to "
                "the case until the tags in the case are updated. To add a tag, take away "
                "the focus of the input field or hit <kbd>Enter</kbd>. <kbd>;</kbd> is "
                "the seperator and will seperate after the tag is entered."
            ),
        },
    }

    #: Additional columns to display for the projects.
    project_list_columns = {
        "states": {
            "title": "States",
            "width": 75,
            "description": "Distribution of case states",
            "align": "center",
            "active": True,
        },
        "cases": {
            "title": "Cases",
            "width": 75,
            "description": "Number of cases in this project",
            "align": "right",
            "active": True,
        },
        "donors": {
            "title": "Donors",
            "width": 75,
            "description": "Number of donors in this project",
            "align": "right",
            "active": True,
        },
        "actions": {
            "title": "Action",
            "width": 75,
            "description": "Execute action",
            "align": "center",
            "active": True,
        },
    }

    def get_project_list_value(self, column_id, project, user):
        if column_id == "cases":
            return Case.objects.filter(project=project).count()
        elif column_id == "donors":
            return sum((len(c.pedigree) for c in Case.objects.filter(project=project)))
        elif column_id == "states":
            return self._get_state_bar_html(project)
        elif column_id == "actions":
            return self._get_action_buttons(project)
        else:
            return "-"

    def _get_state_bar_html(self, project):
        counts = {key: 0 for key, _ in CASE_STATUS_CHOICES}
        for case in Case.objects.filter(project=project):
            counts[case.status] = counts.get(case.status, 0) + 1
        total_count = sum(counts.values())
        total_width = 70
        arr = [
            (
                '<div style="width: {total_width}px; height: 1em; margin-top: .1em; margin-bottom: .1em; '
                'white-space: nowrap;" data-toggle="tooltip" title="initial: %(initial)d, active: %(active)d, '
                "closed&nbsp;(unsolved): %(closed-unsolved)d, closed&nbsp;(uncertain): %(closed-uncertain)d, "
                'closed&nbsp;(solved): %(closed-solved)d">'
            )
            % {"total_width": total_width, **counts}
        ]
        width_sum = 0
        statuses = [k for k, _ in CASE_STATUS_CHOICES if counts.get(k)]  # statuses with counts >0
        if total_count:
            for i, key in enumerate(statuses):
                if i + 1 < len(statuses):
                    width = int(total_width * (counts.get(key, 0) / total_count))
                    width_sum += width
                else:
                    width = total_width - width_sum
                arr.append(
                    '<div style="width:%dpx; height: 100%%; display: inline-block" class="bg-%s"></div>'
                    % (width, case_status_to_color(key))
                )
        else:
            arr.append(
                '<div style="width:%dpx; height: 100%%; display: inline-block" class="bg-%s"></div>'
                % (total_width, case_status_to_color("initial"))
            )
        arr.append("</div>")
        return "".join(arr)

    def _get_action_buttons(self, project):
        tpl = """
        <a href="%s" title="joint filtration " class="btn btn-primary sodar-list-btn sodar-ss-irods-btn">
          <i class="fa fa-filter"></i>
        </a>
        """
        url = reverse("variants:project-cases-filter", kwargs={"project": project.sodar_uuid})
        return tpl % url

    def get_statistics(self):
        return {
            "case_count": {"label": "Cases", "value": Case.objects.all().count()},
            "donor_count": {
                "label": "Donors",
                "value": sum((len(c.pedigree) for c in Case.objects.all())),
            },
        }

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
        elif isinstance(obj, CaseComments):
            return {"url": obj.get_absolute_url(), "label": obj.shortened_text()}
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
        SyncCaseListBgJob.spec_name: SyncCaseListBgJob,
        ImportVariantsBgJob.spec_name: ImportVariantsBgJob,
    }
