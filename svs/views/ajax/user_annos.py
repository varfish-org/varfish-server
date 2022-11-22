"""AJAX views for dealing with user annotations (flags and comments)."""

from projectroles.views_api import SODARAPIGenericProjectMixin, SODARAPIProjectPermission
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from svs.models import StructuralVariantComment, StructuralVariantFlags
from svs.serializers.user_annos import (
    StructuralVariantCommentSerializer,
    StructuralVariantFlagsSerializer,
)
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models import Case


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
        return StructuralVariantFlags.objects.select_related("case").all()

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


class StructuralVariantFlagsRetrieveUpdateDestroyAjaxView(
    StructuralVariantFlagsAjaxMixin, RetrieveUpdateDestroyAPIView
):
    lookup_url_kwarg = "structuralvariantflags"

    permission_classes = [SvUserAnnotationRetrieveUpdateDestroyPermission]


class StructuralVariantCommentAjaxMixin(SvApiBaseMixin):

    serializer_class = StructuralVariantCommentSerializer

    def get_queryset(self):
        return StructuralVariantComment.objects.all()

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
            result[key] = self.request.query_params[key]
        return result


class StructuralVariantCommentRetrieveUpdateDestroyAjaxView(
    StructuralVariantCommentAjaxMixin, RetrieveUpdateDestroyAPIView
):
    lookup_url_kwarg = "structuralvariantcomment"

    permission_classes = [SvUserAnnotationRetrieveUpdateDestroyPermission]
