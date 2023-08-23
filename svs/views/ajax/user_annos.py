"""AJAX views for dealing with user annotations (flags and comments)."""

from iterable_orm import QuerySet
from projectroles.views_api import SODARAPIGenericProjectMixin, SODARAPIProjectPermission
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from svs.models import StructuralVariantComment, StructuralVariantFlags
from svs.serializers.user_annos import (
    StructuralVariantCommentSerializer,
    StructuralVariantFlagsSerializer,
)
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models import Case


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


class StructuralVariantCommentRetrieveUpdateDestroyAjaxView(
    SvApiBaseMixin, RetrieveUpdateDestroyAPIView
):
    lookup_url_kwarg = "structuralvariantcomment"

    serializer_class = StructuralVariantFlagsSerializer
    permission_classes = [SvUserAnnotationRetrieveUpdateDestroyPermission]

    def get_queryset(self):
        return StructuralVariantFlags.objects.all()

    def get_permission_required(self):
        return "variants.update_data"
