"""AJAX views for dealing with user annotations (flags and comments)."""

import sys
import uuid

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from iterable_orm import QuerySet
from projectroles.views_api import SODARAPIGenericProjectMixin, SODARAPIProjectPermission
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView

from svs.models import StructuralVariantComment, StructuralVariantFlags, SvQueryResultRow
from svs.models.user_annos import StructuralVariantAcmgRating
from svs.serializers.user_annos import (
    StructuralVariantAcmgRatingProjectSerializer,
    StructuralVariantAcmgRatingSerializer,
    StructuralVariantCommentProjectSerializer,
    StructuralVariantCommentSerializer,
    StructuralVariantFlagsProjectSerializer,
    StructuralVariantFlagsSerializer,
)
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models import Case
from variants.views.api import CreatedAtCursorPagination


def reciprocal_overlap(*, sv_type: str, qry_start: int, qry_end: int, record) -> float:
    bnd_ins_slack = 50
    if sv_type in ("BND", "INS"):
        if qry_end + bnd_ins_slack > record.start and record.end > qry_start - bnd_ins_slack:
            return 1.0
        else:
            return 0.0
    else:
        ovl_begin = max(record.start, qry_start) - 1
        ovl_end = min(record.end, qry_end)
        if ovl_begin >= ovl_end:
            return 0.0
        else:
            ovl_len = ovl_end - ovl_begin
            qry_len = qry_end - qry_start + 1
            record_len = record.end - record.start + 1
            return min(ovl_len / qry_len, ovl_len / record_len)


def show_in_case_annotation_overview(annotation, result_row_uuid):
    """Show the annotated SV in its case's annotation overview.

    The overview is the case's result set without a query.  It has one row per SV, a
    copy of the result row the SV was annotated from.

    Only a result row of the annotated case at the annotated SV is accepted.  The
    annotation does not match the row in all fields: for breakends, ``chr`` is stripped
    from the chromosome, insertions and breakends have their start as end, and the
    sub type is the SV type.  Call it in the transaction that saves the annotation,
    so that a rejected result row also discards the annotation.
    """
    case = annotation.case
    try:
        result_row = SvQueryResultRow.objects.get(
            # Result sets of queries did not store the case in the past.
            Q(svqueryresultset__case=case) | Q(svqueryresultset__svquery__case=case),
            sodar_uuid=result_row_uuid,
            release=annotation.release,
            chromosome__in=(annotation.chromosome, f"chr{annotation.chromosome}"),
            start=annotation.start,
            sv_type=annotation.sv_type,
        )
    except (SvQueryResultRow.DoesNotExist, DjangoValidationError):
        raise ValidationError(
            detail={"error": "Result row of the annotated case and SV not found."}
        )
    result_set = case.svqueryresultset_set.filter(svquery=None).first()
    try:
        result_set.svqueryresultrow_set.get(
            release=annotation.release,
            chromosome=annotation.chromosome,
            start=annotation.start,
            end=annotation.end,
            sv_type=annotation.sv_type,
            sv_sub_type=annotation.sv_sub_type,
        )
    except SvQueryResultRow.DoesNotExist:
        result_row.pk = None
        result_row.sodar_uuid = uuid.uuid4()
        result_row.svqueryresultset = result_set
        result_row.save()
        result_set.result_row_count += 1
        result_set.save()


class SvUserAnnotationListCreatePermission(SODARAPIProjectPermission):
    """Project-based permission for ``svs`` user annotations list/create AJAX views."""

    def get_project(self, request=None, kwargs=None):
        case = Case.objects.get(sodar_uuid=kwargs["case"])
        return case.project


class SvUserAnnotationRetrieveUpdateDestroyPermission(SODARAPIProjectPermission):
    """Project-based permission for ``svs`` user annotations retrieve/update/destroy AJAX views."""

    def get_project(self, request=None, kwargs=None):
        if "structuralvariantflags" in kwargs:
            structuralvariantflags = StructuralVariantFlags.objects.get(
                sodar_uuid=kwargs["structuralvariantflags"]
            )
            return structuralvariantflags.case.project
        elif "structuralvariantcomment" in kwargs:
            structuralvariantcomment = StructuralVariantComment.objects.get(
                sodar_uuid=kwargs["structuralvariantcomment"]
            )
            return structuralvariantcomment.case.project
        elif "structuralvariantacmgrating" in kwargs:
            structuralvariantacmgrating = StructuralVariantAcmgRating.objects.get(
                sodar_uuid=kwargs["structuralvariantacmgrating"]
            )
            return structuralvariantacmgrating.case.project
        else:
            raise RuntimeError("Must never happen")


class SvApiBaseMixin(SODARAPIGenericProjectMixin):
    """Mixin to enforce project-based permissions."""

    lookup_field = "sodar_uuid"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning


class StructuralVariantFlagsAjaxMixin(SvApiBaseMixin):
    serializer_class = StructuralVariantFlagsSerializer

    def get_queryset(self):
        return StructuralVariantFlags.objects.select_related("case").filter(
            case__sodar_uuid=self.kwargs["case"]
        )

    def get_permission_required(self):
        return "variants.view_data"


class StructuralVariantFlagsListCreateAjaxView(StructuralVariantFlagsAjaxMixin, ListCreateAPIView):
    lookup_url_kwarg = "case"

    permission_classes = [SvUserAnnotationListCreatePermission]

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        keys = ("release", "chromosome", "start", "end", "sv_type", "sv_sub_type")
        for key in keys:
            if key in self.request.query_params:
                result[key] = self.request.query_params[key]
        return result

    def filter_queryset(self, queryset):
        min_reciprocal_overlap = 0.8
        serializer_context = self.get_serializer_context()
        if "start" in serializer_context and "end" in serializer_context:
            start = int(serializer_context["start"])
            end = int(serializer_context["end"])
            all_objs = list(queryset)
            return QuerySet(
                [
                    obj
                    for obj in all_objs
                    if reciprocal_overlap(
                        sv_type=obj.sv_type, qry_start=start, qry_end=end, record=obj
                    )
                    >= min_reciprocal_overlap
                ]
            )
        else:
            return queryset

    def get_queryset(self):
        serializer_context = self.get_serializer_context()
        qs = super().get_queryset()
        keys = ("case", "release", "chromosome", "sv_type", "sv_sub_type")
        query_args = {}
        for key in keys:
            if key in serializer_context:
                query_args[key] = serializer_context[key]
        if query_args:
            qs = qs.filter(**query_args)
        return qs

    def perform_create(self, serializer):
        if not self.request.data.get("sodar_uuid"):
            raise ValidationError(
                detail={
                    "error": "`sodar_uuid` of SvQueryResultRow required. Aborting flag creation."
                }
            )
        with transaction.atomic():
            super().perform_create(serializer)
            show_in_case_annotation_overview(serializer.instance, self.request.data["sodar_uuid"])


class StructuralVariantFlagsListProjectAjaxView(StructuralVariantFlagsAjaxMixin, ListAPIView):
    lookup_url_kwarg = "project"
    serializer_class = StructuralVariantFlagsProjectSerializer

    def get_queryset(self):
        keys = ("release", "chromosome", "start", "end", "sv_type", "sv_sub_type")
        query_set = StructuralVariantFlags.objects.select_related("case__project").filter(
            case__project__sodar_uuid=self.kwargs["project"]
        )

        case_uuid = self.request.GET.get("exclude_case_uuid")

        if case_uuid:
            query_set = query_set.exclude(case__sodar_uuid=case_uuid)

        for key in keys:
            if key not in self.request.GET:
                break
        else:
            query_set = query_set.filter(**{key: self.request.GET[key] for key in keys})

        return query_set.order_by("date_created")


class StructuralVariantFlagsRetrieveUpdateDestroyAjaxView(
    SvApiBaseMixin, RetrieveUpdateDestroyAPIView
):
    lookup_url_kwarg = "structuralvariantflags"

    serializer_class = StructuralVariantFlagsSerializer
    permission_classes = [SvUserAnnotationRetrieveUpdateDestroyPermission]

    def get_queryset(self):
        return StructuralVariantFlags.objects.all()

    def get_permission_required(self):
        return "variants.update_data"

    def perform_destroy(self, instance):
        result_set = instance.case.svqueryresultset_set.filter(svquery=None).first()
        if result_set:
            result_row_set = result_set.svqueryresultrow_set.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                sv_type=instance.sv_type,
            )
            comments = StructuralVariantComment.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                sv_type=instance.sv_type,
            )
            acmg_ratings = StructuralVariantAcmgRating.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                sv_type=instance.sv_type,
            )
            if result_row_set.exists() and not comments.exists() and not acmg_ratings.exists():
                result_row_set.first().delete()
                result_set.result_row_count -= 1
                result_set.save()
        super().perform_destroy(instance)


class StructuralVariantCommentAjaxMixin(SvApiBaseMixin):
    serializer_class = StructuralVariantCommentSerializer

    def get_queryset(self):
        return StructuralVariantComment.objects.filter(case__sodar_uuid=self.kwargs["case"])

    def get_permission_required(self):
        return "variants.view_data"


class StructuralVariantCommentListCreateAjaxView(
    StructuralVariantCommentAjaxMixin, ListCreateAPIView
):
    lookup_url_kwarg = "case"

    permission_classes = [SvUserAnnotationListCreatePermission]

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        keys = ("release", "chromosome", "start", "end", "sv_type", "sv_sub_type")
        for key in keys:
            if key in self.request.query_params:
                result[key] = self.request.query_params[key]
        return result

    def get_queryset(self):
        serializer_context = self.get_serializer_context()
        qs = super().get_queryset()
        keys = ("release", "chromosome", "start", "end", "sv_type", "sv_sub_type")
        query_args = {}
        for key in keys:
            if key in serializer_context:
                query_args[key] = serializer_context[key]
            qs = qs.filter(**query_args)
        return qs

    def perform_create(self, serializer):
        if not self.request.data.get("sodar_uuid"):
            raise ValidationError(
                detail={
                    "error": "`sodar_uuid` of SvQueryResultRow required. Aborting comment creation."
                }
            )

        with transaction.atomic():
            super().perform_create(serializer)
            show_in_case_annotation_overview(serializer.instance, self.request.data["sodar_uuid"])


class StructuralVariantCommentListProjectAjaxView(StructuralVariantCommentAjaxMixin, ListAPIView):
    lookup_url_kwarg = "project"
    serializer_class = StructuralVariantCommentProjectSerializer

    def get_queryset(self):
        keys = ("release", "chromosome", "start", "end", "sv_type", "sv_sub_type")
        query_set = StructuralVariantComment.objects.select_related("user", "case__project").filter(
            case__project__sodar_uuid=self.kwargs["project"]
        )

        case_uuid = self.request.GET.get("exclude_case_uuid")

        if case_uuid:
            query_set = query_set.exclude(case__sodar_uuid=case_uuid)

        for key in keys:
            if key not in self.request.GET:
                break
        else:
            query_set = query_set.filter(**{key: self.request.GET[key] for key in keys})

        return query_set.order_by("date_created")


class StructuralVariantCommentRetrieveUpdateDestroyAjaxView(
    SvApiBaseMixin, RetrieveUpdateDestroyAPIView
):
    lookup_url_kwarg = "structuralvariantcomment"

    serializer_class = StructuralVariantCommentSerializer
    permission_classes = [SvUserAnnotationRetrieveUpdateDestroyPermission]

    def get_queryset(self):
        return StructuralVariantComment.objects.all()

    def get_permission_required(self):
        return "variants.update_data"

    def perform_destroy(self, instance):
        result_set = instance.case.svqueryresultset_set.filter(svquery=None).first()
        if result_set:
            result_row_set = result_set.svqueryresultrow_set.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                sv_type=instance.sv_type,
                sv_sub_type=instance.sv_sub_type,
            )
            flags = StructuralVariantFlags.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                sv_type=instance.sv_type,
                sv_sub_type=instance.sv_sub_type,
            )
            acmg_ratings = StructuralVariantAcmgRating.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                sv_type=instance.sv_type,
                sv_sub_type=instance.sv_sub_type,
            )
            if result_row_set.exists() and not flags.exists() and not acmg_ratings.exists():
                result_row_set.first().delete()
                result_set.result_row_count -= 1
                result_set.save()
        super().perform_destroy(instance)


class StructuralVariantAcmgRatingAjaxMixin(SvApiBaseMixin):
    serializer_class = StructuralVariantAcmgRatingSerializer
    pagination_class = CreatedAtCursorPagination

    def get_queryset(self):
        return StructuralVariantAcmgRating.objects.filter(case__sodar_uuid=self.kwargs["case"])

    def get_permission_required(self):
        return "variants.view_data"


class StructuralVariantAcmgRatingListCreateAjaxView(
    StructuralVariantAcmgRatingAjaxMixin, ListCreateAPIView
):
    lookup_url_kwarg = "case"

    permission_classes = [SvUserAnnotationListCreatePermission]

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        keys = ("release", "chromosome", "start", "end", "sv_type", "sv_sub_type")
        for key in keys:
            if key in self.request.query_params:
                result[key] = self.request.query_params[key]
        return result

    def get_queryset(self):
        serializer_context = self.get_serializer_context()
        qs = super().get_queryset()
        keys = ("release", "chromosome", "start", "end", "sv_type", "sv_sub_type")
        query_args = {}
        for key in keys:
            if key in serializer_context:
                query_args[key] = serializer_context[key]
            qs = qs.filter(**query_args)
        return qs

    def perform_create(self, serializer):
        with transaction.atomic():
            super().perform_create(serializer)
            # Optional, as REST API clients may not send it.
            if self.request.data.get("sodar_uuid"):
                show_in_case_annotation_overview(
                    serializer.instance, self.request.data["sodar_uuid"]
                )


class StructuralVariantAcmgRatingListProjectAjaxView(
    StructuralVariantAcmgRatingAjaxMixin, ListAPIView
):
    lookup_url_kwarg = "project"
    serializer_class = StructuralVariantAcmgRatingProjectSerializer

    def get_queryset(self):
        keys = ("release", "chromosome", "start", "end", "sv_type", "sv_sub_type")
        query_set = StructuralVariantAcmgRating.objects.select_related(
            "user", "case__project"
        ).filter(case__project__sodar_uuid=self.kwargs["project"])

        case_uuid = self.request.GET.get("exclude_case_uuid")

        if case_uuid:
            query_set = query_set.exclude(case__sodar_uuid=case_uuid)

        for key in keys:
            if key not in self.request.GET:
                break
        else:
            query_set = query_set.filter(**{key: self.request.GET[key] for key in keys})

        return query_set.order_by("date_created")


class StructuralVariantAcmgRatingRetrieveUpdateDestroyAjaxView(
    SvApiBaseMixin, RetrieveUpdateDestroyAPIView
):
    lookup_url_kwarg = "structuralvariantacmgrating"

    serializer_class = StructuralVariantAcmgRatingSerializer
    permission_classes = [SvUserAnnotationRetrieveUpdateDestroyPermission]

    def get_queryset(self):
        return StructuralVariantAcmgRating.objects.all()

    def get_permission_required(self):
        return "variants.update_data"

    def perform_destroy(self, instance):
        result_set = instance.case.svqueryresultset_set.filter(svquery=None).first()
        if result_set:
            result_row_set = result_set.svqueryresultrow_set.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                sv_type=instance.sv_type,
                sv_sub_type=instance.sv_sub_type,
            )
            flags = StructuralVariantFlags.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                sv_type=instance.sv_type,
                sv_sub_type=instance.sv_sub_type,
            )
            comments = StructuralVariantComment.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                sv_type=instance.sv_type,
                sv_sub_type=instance.sv_sub_type,
            )
            if result_row_set.exists() and not flags.exists() and not comments.exists():
                result_row_set.first().delete()
                result_set.result_row_count -= 1
                result_set.save()
        super().perform_destroy(instance)
