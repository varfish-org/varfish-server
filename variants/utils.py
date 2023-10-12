import importlib
from itertools import chain
import uuid

from svs.models import (
    StructuralVariantComment,
    StructuralVariantFlags,
    SvQueryResultRow,
    SvQueryResultSet,
)
from variants.models import (
    AcmgCriteriaRating,
    Case,
    SmallVariantComment,
    SmallVariantFlags,
    SmallVariantQueryResultRow,
    SmallVariantQueryResultSet,
)


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
        "svqueryresultset": 0,  # SvQueryResultSet's created
        "smallvariantqueryresultset": 0,  # SmallVariantQueryResultSet's created
    }
    fill_count = {
        "structural_variant_annotations": 0,  # user annotations added to SvQueryResultSet's
        "structural_variant_annotations_orphaned": 0,  # user annotations without corresponding query result row
        "small_variant_annotations": 0,  # user annotations added to SmallVariantQueryResultSet's
        "small_variant_annotations_orphaned": 0,  # user annotations without corresponding query result row
    }
    orphans = {}

    def _perform_create(_case):
        _sm_result_set = _case.smallvariantqueryresultset_set.first()
        _sv_result_set = _case.svqueryresultset_set.first()
        if _sm_result_set is None:
            count["smallvariantqueryresultset"] += 1
            _sm_result_set = SmallVariantQueryResultSet.objects.create(
                case=_case,
                result_row_count=0,
                start_time=_case.date_created,
                end_time=_case.date_created,
                elapsed_seconds=0,
            )
        if _sv_result_set is None:
            count["svqueryresultset"] += 1
            _sv_result_set = SvQueryResultSet.objects.create(
                case=_case,
                result_row_count=0,
                start_time=_case.date_created,
                end_time=_case.date_created,
                elapsed_seconds=0,
            )
        return _sm_result_set, _sv_result_set

    def _perform_fill(sm_result_set, sv_result_set):
        sm_fill_count, sm_orphans = fill_sm_queryresultset(sm_result_set)
        sv_fill_count, sv_orphans = fill_sv_queryresultset(sv_result_set)
        fill_count["structural_variant_annotations"] += sv_fill_count["annotations"]
        fill_count["structural_variant_annotations_orphaned"] += sv_fill_count["orphaned"]
        fill_count["small_variant_annotations"] += sm_fill_count["annotations"]
        fill_count["small_variant_annotations_orphaned"] += sm_fill_count["orphaned"]
        orphans[str(sm_result_set.case.sodar_uuid)] = {
            "small_variants": sm_orphans,
            "structural_variants": sv_orphans,
        }

    if bool(case_uuid) + bool(project_uuid) + bool(all) != 1:
        return

    if case_uuid:
        _case = Case.objects.get(sodar_uuid=case_uuid)
        sm_result_set, sv_result_set = _perform_create(_case)
        _perform_fill(sm_result_set, sv_result_set)
    elif project_uuid:
        for _case in Case.objects.filter(project__sodar_uuid=project_uuid):
            sm_result_set, sv_result_set = _perform_create(_case)
            _perform_fill(sm_result_set, sv_result_set)
    else:
        for _case in Case.objects.all():
            sm_result_set, sv_result_set = _perform_create(_case)
            _perform_fill(sm_result_set, sv_result_set)

    return count, fill_count, orphans


def fill_sm_queryresultset(result_set):
    """Fill a SmallVariantQueryResultSet for the given case or project."""
    case = result_set.case
    count = {
        "annotations": 0,
        "orphaned": 0,
    }
    orphans = []

    def _perform_create(obj):
        coords = {
            "release": obj.release,
            "chromosome": obj.chromosome,
            "start": obj.start,
            "end": obj.end,
            "reference": obj.reference,
            "alternative": obj.alternative,
        }

        try:
            result_set.smallvariantqueryresultrow_set.get(**coords)

        except SmallVariantQueryResultRow.DoesNotExist:
            queries = case.small_variant_queries.all()
            for query in queries:
                query_result_set = query.smallvariantqueryresultset_set.first()
                if not query_result_set:
                    continue
                result_row = query_result_set.smallvariantqueryresultrow_set.filter(**coords)
                if not result_row.exists():
                    continue
                result_row = result_row.first()
                result_row.pk = None
                result_row.sodar_uuid = uuid.uuid4()
                result_row.smallvariantqueryresultset = result_set
                result_row.save()
                count["annotations"] += 1
                break
            else:
                # should exist as it was annotated.
                count["orphaned"] += 1
                orphans.append(
                    "{release}-{chromosome}-{start}-{reference}-{alternative}".format(**coords)
                )

        result_set.result_row_count = result_set.smallvariantqueryresultrow_set.count()
        result_set.save()

    small_variant_flags = SmallVariantFlags.objects.filter(case=case)
    small_variant_comments = SmallVariantComment.objects.filter(case=case)
    acmg_rating = AcmgCriteriaRating.objects.filter(case=case)

    for obj in chain(small_variant_flags, small_variant_comments, acmg_rating):
        _perform_create(obj)

    return count, orphans


def fill_sv_queryresultset(result_set):
    """Fill a SvQueryResultSet for the given case or project."""

    case = result_set.case
    count = {
        "annotations": 0,
        "orphaned": 0,
    }
    orphans = []

    def _perform_create(obj):
        coords = {
            "release": obj.release,
            "chromosome": obj.chromosome,
            "start": obj.start,
            "end": obj.end,
            "sv_type": obj.sv_type,
            "sv_sub_type": obj.sv_sub_type,
        }

        try:
            result_set.svqueryresultrow_set.get(**coords)

        except SvQueryResultRow.DoesNotExist:
            queries = case.svquery_set.all()
            for query in queries:
                query_result_set = query.svqueryresultset_set.first()
                if not query_result_set:
                    continue
                result_row = query_result_set.svqueryresultrow_set.filter(**coords)
                if not result_row.exists():
                    continue
                result_row = result_row.first()
                result_row.pk = None
                result_row.sodar_uuid = uuid.uuid4()
                result_row.svqueryresultset = result_set
                result_row.save()
                count["annotations"] += 1
                break
            else:
                # should exist as it was annotated.
                count["orphaned"] += 1
                orphans.append(
                    "{release}-{chromosome}-{start}-{end}-{sv_type}-{sv_sub_type}".format(**coords)
                )

        result_set.result_row_count = result_set.svqueryresultrow_set.count()
        result_set.save()

    sv_flags = StructuralVariantFlags.objects.filter(case=case)
    sv_comments = StructuralVariantComment.objects.filter(case=case)

    for obj in chain(sv_flags, sv_comments):
        _perform_create(obj)

    return count, orphans
