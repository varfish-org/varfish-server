import importlib

from svs.models import SvQueryResultSet
from variants.models import Case, SmallVariantQueryResultSet


def class_from_string(dot_path):
    """Load a class from the given dot path."""
    if "." in dot_path:
        module_name, class_name = dot_path.rsplit(".", 1)
    else:
        module_name = "."
        class_name = dot_path
    m = importlib.import_module(module_name)
    return getattr(m, class_name)


def create_queryresultset(case_uuid=None, project_uuid=None, all=False):
    """Create a SmallVariantQueryResultSet for the given case or project."""

    count = {
        "svqueryresultset": 0,
        "smallvariantqueryresultset": 0,
    }

    def _perform_create(_case, count):
        if _case.num_small_vars and _case.smallvariantqueryresultset_set.count() == 0:
            count["smallvariantqueryresultset"] += 1
            SmallVariantQueryResultSet.objects.create(
                case=_case,
                result_row_count=0,
                start_time=_case.date_created,
                end_time=_case.date_created,
                elapsed_seconds=0,
            )
        if _case.num_svs and _case.svqueryresultset_set.count() == 0:
            count["svqueryresultset"] += 1
            SvQueryResultSet.objects.create(
                case=_case,
                result_row_count=0,
                start_time=_case.date_created,
                end_time=_case.date_created,
                elapsed_seconds=0,
            )

    if bool(case_uuid) + bool(project_uuid) + bool(all) != 1:
        return

    if case_uuid:
        _perform_create(Case.objects.get(sodar_uuid=case_uuid), count)
    elif project_uuid:
        for _case in Case.objects.filter(project__sodar_uuid=project_uuid):
            _perform_create(_case, count)
    else:
        for _case in Case.objects.all():
            _perform_create(_case, count)

    return count
