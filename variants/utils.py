import importlib
from itertools import chain
import json
import uuid

from django.forms import model_to_dict

from svs.models import (
    StructuralVariant,
    StructuralVariantComment,
    StructuralVariantFlags,
    SvQueryResultSet,
)
from variants.models import (
    AcmgCriteriaRating,
    Case,
    SmallVariant,
    SmallVariantComment,
    SmallVariantFlags,
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
        "svs": {
            "added": 0,  # user annotations added to SvQueryResultSet's
            "removed": 0,  # user annotations without corresponding query result row
            "salvable": {
                "comments": 0,
                "flags": 0,
            },  # user annotations without corresponding query result row
            "lost": {
                "comments": 0,
                "flags": 0,
            },  # user annotations without corresponding query result row
        },
        "sms": {
            "added": 0,
            "removed": 0,
            "salvable": {
                "comments": 0,
                "flags": 0,
                "acmg_ratings": 0,
            },
            "lost": {
                "comments": 0,
                "flags": 0,
                "acmg_ratings": 0,
            },
        },
    }
    salvable = {}
    duplicates = {
        "svs": [],
        "sms": [],
    }
    orphans = {
        "svs": {
            "flags": [],
            "comments": [],
        },
        "sms": {
            "flags": [],
            "comments": [],
            "acmg_ratings": [],
        },
    }

    def _perform_create(_case):
        _sm_result_set = _case.smallvariantqueryresultset_set.filter(smallvariantquery=None)
        _sv_result_set = _case.svqueryresultset_set.filter(svquery=None)

        if _sm_result_set.count() > 1:
            raise ValueError(
                "More than one SmallVariantQueryResultSet without SmallVariantQuery for case {_case.name} {_case.sodar_uuid}"
            )
        elif _sm_result_set.count() == 0:
            count["smallvariantqueryresultset"] += 1
            _sm_result_set = SmallVariantQueryResultSet.objects.create(
                case=_case,
                result_row_count=0,
                start_time=_case.date_created,
                end_time=_case.date_created,
                elapsed_seconds=0,
            )
        else:
            _sm_result_set = _sm_result_set.first()

        if _sv_result_set.count() > 1:
            raise ValueError(
                "More than one SvQueryResultSet without SvQuery for case {_case.name} {_case.sodar_uuid}"
            )
        elif _sv_result_set.count() == 0:
            count["svqueryresultset"] += 1
            _sv_result_set = SvQueryResultSet.objects.create(
                case=_case,
                result_row_count=0,
                start_time=_case.date_created,
                end_time=_case.date_created,
                elapsed_seconds=0,
            )
        else:
            _sv_result_set = _sv_result_set.first()

        return _sm_result_set, _sv_result_set

    def _perform_fill(sm_result_set, sv_result_set):
        sm_count, sm_salvable, sm_duplicates, sm_orphans = fill_sm_queryresultset(sm_result_set)
        sv_count, sv_salvable, sv_duplicates, sv_orphans = fill_sv_queryresultset(sv_result_set)
        for i in (
            "salvable",
            "lost",
        ):
            count["svs"][i]["flags"] += sv_count[i]["flags"]
            count["svs"][i]["comments"] += sv_count[i]["comments"]
            count["sms"][i]["flags"] += sm_count[i]["flags"]
            count["sms"][i]["comments"] += sm_count[i]["comments"]
            count["sms"][i]["acmg_ratings"] += sm_count[i]["acmg_ratings"]
        count["svs"]["added"] += sv_count["added"]
        count["sms"]["added"] += sm_count["added"]
        count["svs"]["removed"] += sv_count["removed"]
        count["sms"]["removed"] += sm_count["removed"]
        if sm_salvable or sv_salvable:
            salvable[str(sm_result_set.case.sodar_uuid)] = {
                "sms": list(set(sm_salvable)),
                "svs": list(set(sv_salvable)),
            }
        duplicates["sms"].extend(sm_duplicates)
        duplicates["svs"].extend(sv_duplicates)
        orphans["sms"]["flags"].extend(sm_orphans["flags"])
        orphans["sms"]["comments"].extend(sm_orphans["comments"])
        orphans["sms"]["acmg_ratings"].extend(sm_orphans["acmg_ratings"])
        orphans["svs"]["flags"].extend(sv_orphans["flags"])
        orphans["svs"]["comments"].extend(sv_orphans["comments"])

    def _perform_clear(sm_result_set, sv_result_set):
        count["sms"]["removed"] += clear_sm_queryresultset(sm_result_set)
        count["svs"]["removed"] += clear_sv_queryresultset(sv_result_set)

    def _handle_case(_case):
        sm_result_set, sv_result_set = _perform_create(_case)
        _perform_clear(sm_result_set, sv_result_set)
        _perform_fill(sm_result_set, sv_result_set)

    if bool(case_uuid) + bool(project_uuid) + bool(all) != 1:
        return

    if case_uuid:
        _case = Case.objects.get(sodar_uuid=case_uuid)
        _handle_case(_case)
    elif project_uuid:
        for _case in Case.objects.filter(project__sodar_uuid=project_uuid):
            _handle_case(_case)
    else:
        for _case in Case.objects.all():
            _handle_case(_case)

    return count, salvable, duplicates, orphans


def fill_sm_queryresultset(result_set):
    """Fill a SmallVariantQueryResultSet for the given case or project."""
    case = result_set.case
    count = {
        "added": 0,
        "removed": 0,
        "salvable": {
            "flags": 0,
            "comments": 0,
            "acmg_ratings": 0,
        },
        "lost": {
            "flags": 0,
            "comments": 0,
            "acmg_ratings": 0,
        },
    }
    salvable = []
    duplicates = []
    orphans = {
        "flags": [],
        "comments": [],
        "acmg_ratings": [],
    }

    def _perform_create(obj):
        obj_type = None
        if isinstance(obj, SmallVariantFlags):
            obj_type = "flags"
        elif isinstance(obj, SmallVariantComment):
            obj_type = "comments"
        elif isinstance(obj, AcmgCriteriaRating):
            obj_type = "acmg_ratings"
        coords = {
            "release": obj.release,
            "chromosome": obj.chromosome,
            "start": obj.start,
            "end": obj.end,
            "reference": obj.reference,
            "alternative": obj.alternative,
        }
        lost = True

        # Sanity check
        if SmallVariant.objects.filter(case_id=case.id, **coords).exists():
            lost = False

        result_rows = result_set.smallvariantqueryresultrow_set.filter(**coords)

        if lost:
            count["lost"][obj_type] += 1
            from variants.views import UUIDEncoder

            orphans[obj_type].append(
                {
                    "case_uuid": str(case.sodar_uuid),
                    "case_name": case.name,
                    "project": case.project.full_title,
                    "chromosome": obj.chromosome,
                    "start": obj.start,
                    "end": obj.end,
                    "lost": lost,
                    "json": json.dumps(model_to_dict(obj, exclude=("id",)), cls=UUIDEncoder),
                }
            )
            for result_row in result_rows:
                count["removed"] += 1
                result_row.delete()
        else:
            if result_rows.count() == 0:
                queries = case.small_variant_queries.filter(
                    smallvariantqueryresultset__isnull=False
                )
                for query in queries:
                    query_result_set = query.smallvariantqueryresultset_set.first()
                    result_row = query_result_set.smallvariantqueryresultrow_set.filter(**coords)
                    if not result_row.exists():
                        continue
                    result_row = result_row.first()
                    result_row.pk = None
                    result_row.sodar_uuid = uuid.uuid4()
                    result_row.smallvariantqueryresultset = result_set
                    result_row.save()
                    count["added"] += 1
                    break
                else:
                    # should exist as it was annotated.
                    count["salvable"][obj_type] += 1
                    salvable.append("{chromosome}:{start}-{end}".format(**coords))
                    from variants.views import UUIDEncoder

                    orphans[obj_type].append(
                        {
                            "case_uuid": str(case.sodar_uuid),
                            "case_name": case.name,
                            "project": case.project.full_title,
                            "chromosome": obj.chromosome,
                            "start": obj.start,
                            "end": obj.end,
                            "lost": lost,
                            "json": json.dumps(
                                model_to_dict(obj, exclude=("id",)), cls=UUIDEncoder
                            ),
                        }
                    )
            elif result_rows.count() > 1:
                from variants.views import UUIDEncoder

                for result_row in result_rows:
                    duplicates.append(
                        {
                            {
                                "case_uuid": str(case.sodar_uuid),
                                "case_name": case.name,
                                "project": case.project.full_title,
                                "chromosome": result_row.chromosome,
                                "start": result_row.start,
                                "end": result_row.end,
                                "json": json.dumps(
                                    model_to_dict(result_row, exclude=("id",)), cls=UUIDEncoder
                                ),
                            }
                        }
                    )

        result_set.result_row_count = result_set.smallvariantqueryresultrow_set.count()
        result_set.save()

    sm_flags = SmallVariantFlags.objects.filter(case=case)
    sm_comments = SmallVariantComment.objects.filter(case=case)
    acmg_rating = AcmgCriteriaRating.objects.filter(case=case)

    for obj in chain(sm_flags, sm_comments, acmg_rating):
        _perform_create(obj)

    return count, salvable, duplicates, orphans


def fill_sv_queryresultset(result_set):
    """Fill a SvQueryResultSet for the given case or project."""

    case = result_set.case
    count = {
        "added": 0,
        "removed": 0,
        "salvable": {
            "flags": 0,
            "comments": 0,
        },
        "lost": {
            "flags": 0,
            "comments": 0,
        },
    }
    salvable = []
    duplicates = []
    orphans = {
        "flags": [],
        "comments": [],
    }

    def _perform_create(obj):
        from svs.views import reciprocal_overlap

        obj_type = None
        if isinstance(obj, StructuralVariantFlags):
            obj_type = "flags"
        elif isinstance(obj, StructuralVariantComment):
            obj_type = "comments"
        lost = True

        for sv_obj in StructuralVariant.objects.filter(
            case_id=case.id, chromosome=obj.chromosome, sv_type=obj.sv_type
        ):
            if (
                reciprocal_overlap(
                    sv_type=obj.sv_type, qry_start=sv_obj.start, qry_end=sv_obj.end, record=obj
                )
                >= 0.8
            ):
                lost = False
                break

        result_rows = [
            row_obj
            for row_obj in result_set.svqueryresultrow_set.filter(
                chromosome=obj.chromosome, sv_type=obj.sv_type
            )
            if reciprocal_overlap(
                sv_type=obj.sv_type, qry_start=row_obj.start, qry_end=row_obj.end, record=obj
            )
            >= 0.8
        ]

        if lost:
            count["lost"][obj_type] += 1
            from variants.views import UUIDEncoder

            orphans[obj_type].append(
                {
                    "case_uuid": str(case.sodar_uuid),
                    "case_name": case.name,
                    "project": case.project.full_title,
                    "chromosome": obj.chromosome,
                    "start": obj.start,
                    "end": obj.end,
                    "lost": lost,
                    "json": json.dumps(model_to_dict(obj, exclude=("id",)), cls=UUIDEncoder),
                }
            )
            for result_row in result_rows:
                count["removed"] += 1
                result_row.delete()
        else:
            if not result_rows:
                queries = case.svquery_set.filter(svqueryresultset__isnull=False)
                for query in queries:
                    query_result_set = query.svqueryresultset_set.first()
                    overlapping_result_rows = [
                        row_obj
                        for row_obj in query_result_set.svqueryresultrow_set.filter(
                            chromosome=obj.chromosome,
                            sv_type=obj.sv_type,
                        )
                        if reciprocal_overlap(
                            sv_type=obj.sv_type,
                            qry_start=row_obj.start,
                            qry_end=row_obj.end,
                            record=obj,
                        )
                        >= 0.8
                    ]
                    if not overlapping_result_rows:
                        continue
                    for overlapping_result_row in overlapping_result_rows:
                        overlapping_result_row.pk = None
                        overlapping_result_row.sodar_uuid = uuid.uuid4()
                        overlapping_result_row.svqueryresultset = result_set
                        overlapping_result_row.save()
                        count["added"] += 1
                    break
                else:
                    # should exist as it was annotated.
                    count["salvable"][obj_type] += 1
                    salvable.append(
                        "{chromosome}:{start}-{end}".format(
                            chromosome=obj.chromosome,
                            start=obj.start,
                            end=obj.end,
                        )
                    )
                    from variants.views import UUIDEncoder

                    orphans[obj_type].append(
                        {
                            "case_uuid": str(case.sodar_uuid),
                            "case_name": case.name,
                            "project": case.project.full_title,
                            "chromosome": obj.chromosome,
                            "start": obj.start,
                            "end": obj.end,
                            "lost": lost,
                            "json": json.dumps(
                                model_to_dict(obj, exclude=("id",)), cls=UUIDEncoder
                            ),
                        }
                    )
            elif len(result_rows) > 1:
                from variants.views import UUIDEncoder

                for result_row in result_rows:
                    duplicates.append(
                        {
                            "case_uuid": str(case.sodar_uuid),
                            "case_name": case.name,
                            "project": case.project.full_title,
                            "chromosome": result_row.chromosome,
                            "start": result_row.start,
                            "end": result_row.end,
                            "json": json.dumps(
                                model_to_dict(result_row, exclude=("id",)), cls=UUIDEncoder
                            ),
                        }
                    )

        result_set.result_row_count = result_set.svqueryresultrow_set.count()
        result_set.save()

    sv_flags = StructuralVariantFlags.objects.filter(case=case)
    sv_comments = StructuralVariantComment.objects.filter(case=case)

    for obj in chain(sv_flags, sv_comments):
        _perform_create(obj)

    return count, salvable, duplicates, orphans


def clear_sm_queryresultset(result_set):
    count = 0
    check_for_existence = [
        SmallVariantFlags,
        SmallVariantComment,
        AcmgCriteriaRating,
    ]

    for row in result_set.smallvariantqueryresultrow_set.all():
        row_deleted = False
        for _class in check_for_existence:
            obj = _class.objects.filter(
                case=result_set.case,
                release=row.release,
                chromosome=row.chromosome,
                start=row.start,
                end=row.end,
                reference=row.reference,
                alternative=row.alternative,
            )
            if obj.exists():
                break
        else:
            count += 1
            row_deleted = True
            row.delete()
        if row_deleted:
            continue
        obj = SmallVariant.objects.filter(
            case_id=result_set.case.id,
            release=row.release,
            chromosome=row.chromosome,
            start=row.start,
            end=row.end,
            reference=row.reference,
            alternative=row.alternative,
        )
        if not obj.exists():
            count += 1
            row.delete()
    return count


def clear_sv_queryresultset(result_set):
    from svs.views import reciprocal_overlap

    count = 0
    check_for_existence = [
        StructuralVariantFlags,
        StructuralVariantComment,
    ]

    for row in result_set.svqueryresultrow_set.all():
        row_deleted = False
        for _class in check_for_existence:
            result_row = [
                obj
                for obj in _class.objects.filter(
                    case=result_set.case, chromosome=row.chromosome, sv_type=row.sv_type
                )
                if reciprocal_overlap(
                    sv_type=row.sv_type,
                    qry_start=obj.start,
                    qry_end=obj.end,
                    record=row,
                )
                >= 0.8
            ]
            if result_row:
                break
        else:
            count += 1
            row_deleted = True
            row.delete()
        if row_deleted:
            continue
        result_row = [
            obj
            for obj in StructuralVariant.objects.filter(
                case_id=result_set.case.id, chromosome=row.chromosome, sv_type=row.sv_type
            )
            if reciprocal_overlap(
                sv_type=row.sv_type,
                qry_start=obj.start,
                qry_end=obj.end,
                record=row,
            )
            >= 0.8
        ]
        if not result_row:
            count += 1
            row.delete()
    return count
