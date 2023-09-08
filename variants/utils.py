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
        "structural_variants": 0,  # user annotations added to SvQueryResultSet's
        "structural_variants_orphaned": 0,  # user annotations without corresponding query result row
        "structural_variants_no_query_result_set": 0,  # query without result set
        "structural_variants_no_case_result_set": 0,  # case without result set
        "small_variants": 0,  # user annotations added to SmallVariantQueryResultSet's
        "small_variants_orphaned": 0,  # user annotations without corresponding query result row
        "small_variants_no_query_result_set": 0,  # query without result set
        "small_variants_no_case_result_set": 0,  # case without result set
    }

    def _perform_create(_case):
        if _case.smallvariantqueryresultset_set.count() == 0:
            count["smallvariantqueryresultset"] += 1
            SmallVariantQueryResultSet.objects.create(
                case=_case,
                result_row_count=0,
                start_time=_case.date_created,
                end_time=_case.date_created,
                elapsed_seconds=0,
            )
        if _case.svqueryresultset_set.count() == 0:
            count["svqueryresultset"] += 1
            SvQueryResultSet.objects.create(
                case=_case,
                result_row_count=0,
                start_time=_case.date_created,
                end_time=_case.date_created,
                elapsed_seconds=0,
            )

    def _perform_fill(_case):
        _fill_count = fill_queryresultset(_case)
        fill_count["structural_variants"] += _fill_count["structural_variants"]
        fill_count["structural_variants_orphaned"] += _fill_count["structural_variants_orphaned"]
        fill_count["structural_variants_no_query_result_set"] += _fill_count[
            "structural_variants_no_query_result_set"
        ]
        fill_count["structural_variants_no_case_result_set"] += _fill_count[
            "structural_variants_no_case_result_set"
        ]
        fill_count["small_variants"] += _fill_count["small_variants"]
        fill_count["small_variants_orphaned"] += _fill_count["small_variants_orphaned"]
        fill_count["small_variants_no_query_result_set"] += _fill_count[
            "small_variants_no_query_result_set"
        ]
        fill_count["small_variants_no_case_result_set"] += _fill_count[
            "small_variants_no_case_result_set"
        ]

    if bool(case_uuid) + bool(project_uuid) + bool(all) != 1:
        return

    if case_uuid:
        _case = Case.objects.get(sodar_uuid=case_uuid)
        _perform_create(_case)
        _perform_fill(_case)
    elif project_uuid:
        for _case in Case.objects.filter(project__sodar_uuid=project_uuid):
            _perform_create(_case)
            _perform_fill(_case)
    else:
        for _case in Case.objects.all():
            _perform_create(_case)
            _perform_fill(_case)
    return count, fill_count


# flake8: noqa: C901
def fill_queryresultset(case):
    """Fill a SmallVariantQueryResultSet for the given case or project."""

    count = {
        "structural_variants": 0,
        "structural_variants_orphaned": 0,
        "structural_variants_no_query_result_set": 0,
        "structural_variants_no_case_result_set": 0,
        "small_variants": 0,
        "small_variants_orphaned": 0,
        "small_variants_no_query_result_set": 0,
        "small_variants_no_case_result_set": 0,
    }

    def _perform_create(obj):
        coords = {
            "release": obj.release,
            "chromosome": obj.chromosome,
            "start": obj.start,
            "end": obj.end,
            "reference": obj.reference,
            "alternative": obj.alternative,
        }
        case_result_set = case.smallvariantqueryresultset_set.first()

        if not case_result_set:
            count["small_variants_no_case_result_set"] += 1
            return

        try:
            case_result_set.smallvariantqueryresultrow_set.get(**coords)

        except SmallVariantQueryResultRow.DoesNotExist:
            queries = case.small_variant_queries.all()
            if not queries.exists():
                count["small_variants_orphaned"] += 1
            for query in queries:
                query_result_set = query.smallvariantqueryresultset_set.first()
                if not query_result_set:
                    count["small_variants_no_query_result_set"] += 1
                    continue
                result_row = query_result_set.smallvariantqueryresultrow_set.filter(**coords)
                if not result_row.exists():
                    # should exist as it was annotated.
                    count["small_variants_orphaned"] += 1
                    continue
                result_row = result_row.first()
                result_row.pk = None
                result_row.sodar_uuid = uuid.uuid4()
                result_row.smallvariantqueryresultset = case_result_set
                result_row.save()
                count["small_variants"] += 1

        case_result_set.result_row_count = case_result_set.smallvariantqueryresultrow_set.count()
        case_result_set.save()

    def _perform_create_sv(obj):
        coords = {
            "release": obj.release,
            "chromosome": obj.chromosome,
            "start": obj.start,
            "end": obj.end,
            "sv_type": obj.sv_type,
            "sv_sub_type": obj.sv_sub_type,
        }
        case_result_set = case.svqueryresultset_set.first()

        if not case_result_set:
            count["structural_variants_no_case_result_set"] += 1
            return

        try:
            case_result_set.svqueryresultrow_set.get(**coords)

        except SvQueryResultRow.DoesNotExist:
            queries = case.svquery_set.all()
            if not queries.exists():
                count["structural_variants_orphaned"] += 1
            for query in queries:
                query_result_set = query.svqueryresultset_set.first()
                if not query_result_set:
                    count["structural_variants_no_query_result_set"] += 1
                    continue
                result_row = query_result_set.svqueryresultrow_set.filter(**coords)
                if not result_row.exists():
                    # should exist as it was annotated.
                    count["structural_variants_orphaned"] += 1
                    continue
                result_row = result_row.first()
                result_row.pk = None
                result_row.sodar_uuid = uuid.uuid4()
                result_row.svqueryresultset = case_result_set
                result_row.save()
                count["structural_variants"] += 1

        case_result_set.result_row_count = case_result_set.svqueryresultrow_set.count()
        case_result_set.save()

    small_variant_flags = SmallVariantFlags.objects.filter(case=case)
    small_variant_comments = SmallVariantComment.objects.filter(case=case)
    acmg_rating = AcmgCriteriaRating.objects.filter(case=case)
    sv_flags = StructuralVariantFlags.objects.filter(case=case)
    sv_comments = StructuralVariantComment.objects.filter(case=case)

    for obj in chain(small_variant_flags, small_variant_comments, acmg_rating):
        _perform_create(obj)

    for obj in chain(sv_flags, sv_comments):
        _perform_create_sv(obj)

    return count
