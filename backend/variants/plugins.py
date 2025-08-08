"""Definition of plugins and plugin points."""

from bgjobs.plugins import BackgroundJobsPluginPoint
from django.utils.functional import lazy
from djangoplugins.point import PluginPoint
from projectroles.constants import get_sodar_constants
from projectroles.plugins import ProjectAppPluginPoint

from variants.models import (
    CASE_STATUS_CHOICES,
    CaddSubmissionBgJob,
    Case,
    CaseComments,
    ClearExpiredExportedFilesBgJob,
    ClearInactiveVariantSetsBgJob,
    ClearOldKioskCasesBgJob,
    ComputeProjectVariantsStatsBgJob,
    DistillerSubmissionBgJob,
    ExportFileBgJob,
    ExportProjectCasesFileBgJob,
    FilterBgJob,
    ImportVariantsBgJob,
    ProjectCasesFilterBgJob,
    RefreshSmallVariantSummaryBgJob,
    SmallVariantComment,
    SmallVariantFlags,
    SpanrSubmissionBgJob,
    SyncCaseListBgJob,
)
from variants.templatetags.variants_tags import case_status_to_color


def get_urlpatterns():
    """Return urlpatterns for this URL, to be used with ``lazy()`` to get around circular import."""
    from variants.urls import urlpatterns  # noqa

    return urlpatterns


# Global SODAR constants
SODAR_CONSTANTS = get_sodar_constants()


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "variants"
    title = "Variants"
    urls = lazy(get_urlpatterns, list)()
    # ...

    icon = "mdi:hospital-building"

    entry_point_url_id = "cases:entrypoint"

    description = "Variants"

    #: Required permission for accessing the app
    app_permission = "variants.view_data"

    #: Enable or disable general search from project title bar
    search_enable = False

    #: List of search object types for the app
    search_types = []

    #: Search results template
    search_template = None

    #: App card template for the project details page
    details_template = None

    #: App card title for the project details page
    details_title = "Variants"

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
        "ga4gh_beacon_network_widget_enabled": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_USER"],
            "type": "BOOLEAN",  # STRING/INTEGER/BOOLEAN
            "default": False,
            "label": "GA4GH Beacon Network Widget",
            "description": (
                "Enable GA4GH beacon widget. Please note that your variant query will currently be "
                "sent to all beacons on the network."
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
                "the separator and will separate after the tag is entered."
            ),
        },
        "disable_pedigree_sex_check": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "BOOLEAN",
            "default": False,
            "label": "Disable pedigree sex check",
            "description": (
                "Disable sex check in pedigree. This way, no warning will be displayed when the "
                "reported sex in the pedigree doesn't match the molecular sex signature. "
                "Use this if the sex is unknown."
            ),
        },
        "exclude_from_inhouse_db": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "BOOLEAN",
            "default": False,
            "label": "Exclude from in-house database",
            "description": (
                "Exclude project's cases from in-house database.  This is intended to be used for cases containing "
                "training data that may exist with multiple copies and thus introduce artifacts in the in-house "
                "database (such as no variant of a case showing up because being in the in-house database many times)."
            ),
        },
        "ts_tv_valid_range": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "STRING",
            "default": "2.0-2.9",
            "label": "Ts/Tv valid range",
            "description": (
                "Variants with a Ts/Tv ratio outside this range will be highlighted as a warning. "
                "The recommended value is <code>2.0-2.9</code>"
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
                'closed&nbsp;(partially-solved): %(closed-partially-solved)d, closed&nbsp;(solved): %(closed-solved)d">'
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
        return """
        <span
          class="btn btn-primary sodar-list-btn sodar-ss-irods-btn disabled"
          title="Currently unavailable.">
          <i class="iconify" data-icon="mdi:filter"></i>
        </span>
        """

    def get_statistics(self):
        return {
            "case_count": {"label": "Cases", "value": Case.objects.all().count()},
            "donor_count": {
                "label": "Donors",
                "value": sum((len(c.pedigree) for c in Case.objects.all())),
            },
        }

    def search(self, search_terms, user, search_type=None, keywords=None):
        """
        Return app items based on a search term, user, optional type and
        optional keywords
        :param search_terms: List of strings.
        :param user: User object for user initiating the search
        :param search_type: String
        :param keywords: List (optional)
        :return: Dict
        """
        items = []

        if not search_type:
            cases = Case.objects.find(search_terms, keywords)
            items = [case for case in cases if user.has_perm("variants.view_data", case.project)]
            items.sort(key=lambda x: x.name.lower())
        elif search_type == "case":
            items = Case.objects.find(search_terms, keywords).order_by("name")

        return {"all": {"title": "Cases", "search_types": ["case"], "items": items}}

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
        CaddSubmissionBgJob.spec_name: CaddSubmissionBgJob,
        SpanrSubmissionBgJob.spec_name: SpanrSubmissionBgJob,
        DistillerSubmissionBgJob.spec_name: DistillerSubmissionBgJob,
        ComputeProjectVariantsStatsBgJob.spec_name: ComputeProjectVariantsStatsBgJob,
        ExportProjectCasesFileBgJob.spec_name: ExportProjectCasesFileBgJob,
        FilterBgJob.spec_name: FilterBgJob,
        ProjectCasesFilterBgJob.spec_name: ProjectCasesFilterBgJob,
        SyncCaseListBgJob.spec_name: SyncCaseListBgJob,
        ImportVariantsBgJob.spec_name: ImportVariantsBgJob,
        ClearExpiredExportedFilesBgJob.spec_name: ClearExpiredExportedFilesBgJob,
        ClearInactiveVariantSetsBgJob.spec_name: ClearInactiveVariantSetsBgJob,
        ClearOldKioskCasesBgJob.spec_name: ClearOldKioskCasesBgJob,
        RefreshSmallVariantSummaryBgJob.spec_name: RefreshSmallVariantSummaryBgJob,
    }

    def get_extra_data_link(self, extra_data, name):
        """Return link for the given label that started with ``"extra-"``."""
        if name == "extra-flag_values":
            return extra_data["flag_values"]
        else:
            return "(unknown %s)" % name

    def get_object_link(self, *args, **kwargs):
        return None


##
## Plugin Point Definitions
##


class VariantsExtendQueryInfoColPluginPoint(PluginPoint):
    """Variants plugin point for hooking into the query to extend the query with informative columns.

    These columns can be displayed to the user in the results table but not be used for filtering.  This
    is used in the ``varannos`` app, for example, to add the number of ``VarAnnoSetEntry`` records for a
    variant to the result table.

    CAUTION: Please note that the API is currently not stable yet.
    """

    #: Column definition
    #:
    #: Example ::
    #:
    #: columns = [
    #:   {
    #:     "field_name": "field_name_from_query_result",
    #:     "label": "User-facing label",
    #:   },
    #:   {
    #:     "field_name": "field_name_from_query_result_2",
    #:     "label": "User-facing label #2",
    #:   },
    #: ]
    columns = []

    #: Definition of extra ``ExtendQueryPartsBase`` sub classes for augmenting the query.
    #:
    #: You can also pass a string with the path to the class to break circular dependencies.
    #:
    #: Examples ::
    #:
    #: def extend_query_part_classes(self):
    #:     return [ExtendQueryPartsVarAnnosJoin]
    #:
    #: def extend_query_part_classes(self):
    #:     return ['varannos.queries.ExtendQueryPartsVarAnnosJoin']
    def get_extend_query_part_classes(self):
        return []

    #: Specify explicit ordering.
    plugin_ordering = 100


class VariantsDetailsPluginPoint(PluginPoint):
    """Variants plugin point to add information to the variant details fold-out/modal.

    The output can have certain structures (that are currently subject to change) that will be displayed
    to the user as appropriate.

    CAUTION: Please note that the API is currently not stable yet.
    """

    #: Specify explicit ordering.
    plugin_ordering = 100

    def load_details(
        self,
        *,
        case,
        release,
        chromosome,
        start,
        end,
        reference,
        alternative,
        database,
        gene_id,
        ensembl_transcript_id,
        **kwargs
    ):
        """Load variant details and return a dict with the information.

        :param case: SODAR UUID of the case.
        :param release: Genome release.
        :param chromosome: Chromosome name.
        :param start: Integer start position.
        :param end: Integer end position.
        :param reference: Reference bases.
        :param alternative: Alternative bases.
        :param database: Database name, "refseq" or "ensembl".
        :param gene_id: Gene identifier (Entrez or ENSEMBL gene ID).
        :param ensembl_transcript_id: ENSEMBL transcript ID.
        :param kwargs: The API might change so you should specify a ``kwargs``.
        :return: Dict with "appropriate" structure.
        """

        _ = case
        _ = release
        _ = chromosome
        _ = start
        _ = end
        _ = reference
        _ = alternative
        _ = database
        _ = gene_id
        _ = ensembl_transcript_id
        _ = kwargs

        return {
            "title": "Card Title",
            "plugin_type": "variant",  # currently unused
            "help_text": "This help text is displayed if provided",
            "content": [  # a list of items
                {"label": "first label", "value": "first value"},
                {"label": "second label", "value": "second value"},
            ],
        }


##
## API
##


# Local constants
PLUGIN_TYPE_EXTEND_QUERY_INFO = "extend_query_info"
PLUGIN_TYPE_VARIANT_DETAILS_INFO = "variant_details_info"
PLUGIN_TYPES = {
    "extend_query_info": "VariantsExtendQueryInfoColPluginPoint",
    "variant_details_info": "VariantsDetailsPluginPoint",
}

# From djangoplugins
ENABLED = 0
DISABLED = 1
REMOVED = 2


def get_active_plugins(plugin_type, custom_order=False):
    """
    Return active plugins of a specific type.
    :param plugin_type: "extend_query_info" or "variant_details_info" (string)
    :param custom_order: Order by plugin_ordering for project apps (boolean)
    :return: List or None
    :raise: ValueError if plugin_type is not recognized
    """
    if plugin_type not in PLUGIN_TYPES.keys():
        raise ValueError(
            "Invalid value for plugin_type. Accepted values: {}".format(
                ", ".join(PLUGIN_TYPES.keys())
            )
        )

    plugins = eval(PLUGIN_TYPES[plugin_type]).get_plugins()

    if plugins:
        return sorted(
            [p for p in plugins if p.is_active()],
            key=lambda x: x.plugin_ordering if custom_order else x.name,
        )

    return None


def change_plugin_status(name, status, plugin_type="app"):
    """
    Change the status of a selected plugin in the database.

    :param name: Plugin name (string)
    :param status: Status (int, see djangoplugins)
    :param plugin_type: Type of plugin ("extend_query_info" or "variant_details_info")
    :raise: ValueError if plugin_type is invalid or plugin with name not found
    """
    # NOTE: Used to forge plugin to a specific status for e.g. testing
    if plugin_type == "app":
        plugin = ProjectAppPluginPoint.get_plugin(name)
    elif plugin_type == "extend_query_info":
        plugin = VariantsExtendQueryInfoColPluginPoint.get_plugin(name)
    elif plugin_type == "variant_details_info":
        plugin = VariantsDetailsPluginPoint.get_plugin(name)
    else:
        raise ValueError('Invalid plugin_type: "{}"'.format(plugin_type))

    if not plugin:
        raise ValueError('Plugin of type "{}" not found with name "{}"'.format(plugin_type, name))

    plugin = plugin.get_model()
    plugin.status = status
    plugin.save()
