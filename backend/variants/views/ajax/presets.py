"""Views related to the presets."""

import sys

from projectroles.models import Project
from projectroles.views import LoginRequiredMixin
from projectroles.views_api import SODARAPIGenericProjectMixin, SODARAPIProjectPermission
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models import (
    ChromosomePresets,
    FlagsEtcPresets,
    FrequencyPresets,
    ImpactPresets,
    PresetSet,
    QualityPresets,
    QuickPresets,
)
from variants.serializers import (
    ChromosomePresetsSerializer,
    FlagsEtcPresetsSerializer,
    FrequencyPresetsSerializer,
    ImpactPresetsSerializer,
    PresetSetSerializer,
    QualityPresetsSerializer,
    QuickPresetsSerializer,
)


class _BaseMixin:
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    authentication_classes = [SessionAuthentication]
    permission_classes = [SODARAPIProjectPermission]


class _ListCreateMixin(_BaseMixin):
    def get_permission_required(self):
        if self.request.method == "POST":
            return "variants.add_presets"
        else:
            return "variants.view_presets"


class _RetrieveUpdateDestroyMixin(_BaseMixin):
    def get_permission_required(self):
        if self.request.method == "GET":
            return "variants.view_presets"
        elif self.request.method == "DELETE":
            return "variants.delete_presets"
        else:
            return "variants.update_presets"


class _PresetSetMemberMixinBase:
    def get_serializer_context(self, *args, **kwargs):
        result = super().get_serializer_context(*args, **kwargs)
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["presetset"] = self.get_presetset()
        return result


class _PresetSetMemberMixinListCreate(_PresetSetMemberMixinBase):
    def get_presetset(self):
        return PresetSet.objects.get(sodar_uuid=self.kwargs["presetset"])


class _PresetSetMemberMixinCreateRetrieveDestroy(_PresetSetMemberMixinBase):
    def get_presetset(self):
        return self.get_object().presetset


class _PresetSetMemberCloneOtherPermission(SODARAPIProjectPermission):
    def get_project(self, request=None, kwargs=None):
        presetset = PresetSet.objects.get(sodar_uuid=request.data["presetset"])
        return presetset.project


class FrequencyPresetsListCreateAjaxView(
    _ListCreateMixin,
    _PresetSetMemberMixinListCreate,
    SODARAPIGenericProjectMixin,
    ListCreateAPIView,
):
    """Create & list ``FrequencyPresets`` objects.

    **URL:** ``/variants/ajax/frequencypresets/list-create/<uuid:presetset>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "presetset"

    schema = None
    serializer_class = FrequencyPresetsSerializer

    def get_queryset(self):
        return FrequencyPresets.objects.filter(presetset=self.get_presetset())


class FrequencyPresetsRetrieveUpdateDestroyAjaxView(
    _RetrieveUpdateDestroyMixin,
    _PresetSetMemberMixinCreateRetrieveDestroy,
    SODARAPIGenericProjectMixin,
    RetrieveUpdateDestroyAPIView,
):
    """Allow retrieval, update, destruction of ``FrequencyPresets``.

    **URL:** ``/variants/ajax/frequencypresets/retrieve-update-destroy/<uuid:frequencypresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "frequencypresets"

    schema = None
    serializer_class = FrequencyPresetsSerializer

    def get_queryset(self):
        return FrequencyPresets.objects.all()


class FrequencyPresetsCloneFactoryPresetsAjaxView(
    _ListCreateMixin, SODARAPIGenericProjectMixin, CreateModelMixin, GenericAPIView
):
    """Clone factory presets.

    You must pass in a target PresetSet UUID as ``presetset``.

    **Method:** POST

    **URL:** ``/variants/ajax/frequency/clone-factory-presets/{name}/``
    """

    schema = None
    serializer_class = FrequencyPresetsSerializer

    permission_classes = [_PresetSetMemberCloneOtherPermission]

    def post(self, request, *args, **kwargs):
        target_presetset = PresetSet.objects.get(sodar_uuid=request.data["presetset"])
        instance = FrequencyPresets.objects.create_as_copy_of_factory_preset(
            self.kwargs["name"], request.data["label"], target_presetset
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        presetset = PresetSet.objects.get(sodar_uuid=self.request.data["presetset"])
        return presetset.project

    def get_queryset(self):
        return FrequencyPresets.objects.all()


class FrequencyPresetsCloneOtherAjaxView(
    _ListCreateMixin,
    SODARAPIGenericProjectMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericAPIView,
):
    """Clone other preset set, by default in same project.

    Override target PresetSet with ``presetset``.

    **Method:** POST

    **URL:** ``/variants/ajax/frequencypresets/clone-other/<uuid:frequencypresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "frequencypresets"

    schema = None
    serializer_class = FrequencyPresetsSerializer

    def post(self, request, *args, **kwargs):
        source_obj = self.get_object()
        target_presetset = source_obj.presetset
        if request.data.get("presetset"):
            target_presetset = get_object_or_404(
                PresetSet.objects.all(), sodar_uuid=request.data.get("presetset")
            )
        patch = {}
        if request.data.get("label"):
            patch["label"] = request.data.get("label")
        instance = FrequencyPresets.objects.create_as_copy_of_other_preset(
            source_obj, presetset=target_presetset, **patch
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        presetset = PresetSet.objects.get(sodar_uuid=self.request.data["presetset"])
        return presetset.project

    def get_queryset(self):
        return FrequencyPresets.objects.all()


class ImpactPresetsListCreateAjaxView(
    _ListCreateMixin,
    _PresetSetMemberMixinListCreate,
    SODARAPIGenericProjectMixin,
    ListCreateAPIView,
):
    """Create & list ``ImpactPresets`` objects.

    **URL:** ``/variants/ajax/impactpresets/list-create/<uuid:presetset>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "presetset"

    schema = None
    serializer_class = ImpactPresetsSerializer

    def get_queryset(self):
        return ImpactPresets.objects.filter(presetset=self.get_presetset())


class ImpactPresetsRetrieveUpdateDestroyAjaxView(
    _RetrieveUpdateDestroyMixin,
    _PresetSetMemberMixinCreateRetrieveDestroy,
    SODARAPIGenericProjectMixin,
    RetrieveUpdateDestroyAPIView,
):
    """Allow retrieval, update, destruction of ``ImpactPresets``.

    **URL:** ``/variants/ajax/impactpresets/retrieve-update-destroy/<uuid:impactpresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "impactpresets"

    schema = None
    serializer_class = ImpactPresetsSerializer

    def get_queryset(self):
        return ImpactPresets.objects.all()


class ImpactPresetsCloneFactoryPresetsAjaxView(
    _ListCreateMixin, SODARAPIGenericProjectMixin, CreateModelMixin, GenericAPIView
):
    """Clone factory presets.

    You must pass in a target PresetSet UUID as ``presetset``.

    **Method:** POST

    **URL:** ``/variants/ajax/impact/clone-factory-presets/{name}/``
    """

    schema = None
    serializer_class = ImpactPresetsSerializer

    permission_classes = [_PresetSetMemberCloneOtherPermission]

    def post(self, request, *args, **kwargs):
        target_presetset = PresetSet.objects.get(sodar_uuid=request.data["presetset"])
        instance = ImpactPresets.objects.create_as_copy_of_factory_preset(
            self.kwargs["name"], request.data["label"], target_presetset
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        presetset = PresetSet.objects.get(sodar_uuid=self.request.data["presetset"])
        return presetset.project

    def get_queryset(self):
        return ImpactPresets.objects.all()


class ImpactPresetsCloneOtherAjaxView(
    _ListCreateMixin,
    SODARAPIGenericProjectMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericAPIView,
):
    """Clone other preset set, by default in same project.

    Override target PresetSet with ``presetset``.

    **Method:** POST

    **URL:** ``/variants/ajax/impactpresets/clone-other/<uuid:impactpresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "impactpresets"

    schema = None
    serializer_class = ImpactPresetsSerializer

    def post(self, request, *args, **kwargs):
        source_obj = self.get_object()
        target_presetset = source_obj.presetset
        if request.data.get("presetset"):
            target_presetset = get_object_or_404(
                PresetSet.objects.all(), sodar_uuid=request.data.get("presetset")
            )
        patch = {}
        if request.data.get("label"):
            patch["label"] = request.data.get("label")
        instance = ImpactPresets.objects.create_as_copy_of_other_preset(
            source_obj, presetset=target_presetset, **patch
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        presetset = PresetSet.objects.get(sodar_uuid=self.request.data["presetset"])
        return presetset.project

    def get_queryset(self):
        return ImpactPresets.objects.all()


class QualityPresetsListCreateAjaxView(
    _ListCreateMixin,
    _PresetSetMemberMixinListCreate,
    SODARAPIGenericProjectMixin,
    ListCreateAPIView,
):
    """Create & list ``QualityPresets`` objects.

    **URL:** ``/variants/ajax/qualitypresets/list-create/<uuid:presetset>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "presetset"

    schema = None
    serializer_class = QualityPresetsSerializer

    def get_queryset(self):
        return QualityPresets.objects.filter(presetset=self.get_presetset())


class QualityPresetsRetrieveUpdateDestroyAjaxView(
    _RetrieveUpdateDestroyMixin,
    _PresetSetMemberMixinCreateRetrieveDestroy,
    SODARAPIGenericProjectMixin,
    RetrieveUpdateDestroyAPIView,
):
    """Allow retrieval, update, destruction of ``QualityPresets``.

    **URL:** ``/variants/ajax/qualitypresets/retrieve-update-destroy/<uuid:qualitypresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "qualitypresets"

    schema = None
    serializer_class = QualityPresetsSerializer

    def get_queryset(self):
        return QualityPresets.objects.all()


class QualityPresetsCloneFactoryPresetsAjaxView(
    _ListCreateMixin, SODARAPIGenericProjectMixin, CreateModelMixin, GenericAPIView
):
    """Clone factory presets.

    You must pass in a target PresetSet UUID as ``presetset``.

    **Method:** POST

    **URL:** ``/variants/ajax/quality/clone-factory-presets/{name}/``
    """

    schema = None
    serializer_class = QualityPresetsSerializer

    permission_classes = [_PresetSetMemberCloneOtherPermission]

    def post(self, request, *args, **kwargs):
        target_presetset = PresetSet.objects.get(sodar_uuid=request.data["presetset"])
        instance = QualityPresets.objects.create_as_copy_of_factory_preset(
            self.kwargs["name"], request.data["label"], target_presetset
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        presetset = PresetSet.objects.get(sodar_uuid=self.request.data["presetset"])
        return presetset.project

    def get_queryset(self):
        return QualityPresets.objects.all()


class QualityPresetsCloneOtherAjaxView(
    _ListCreateMixin,
    SODARAPIGenericProjectMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericAPIView,
):
    """Clone other preset set, by default in same project.

    Override target PresetSet with ``presetset``.

    **Method:** POST

    **URL:** ``/variants/ajax/qualitypresets/clone-other/<uuid:qualitypresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "qualitypresets"

    schema = None
    serializer_class = QualityPresetsSerializer

    def post(self, request, *args, **kwargs):
        source_obj = self.get_object()
        target_presetset = source_obj.presetset
        if request.data.get("presetset"):
            target_presetset = get_object_or_404(
                PresetSet.objects.all(), sodar_uuid=request.data.get("presetset")
            )
        patch = {}
        if request.data.get("label"):
            patch["label"] = request.data.get("label")
        instance = QualityPresets.objects.create_as_copy_of_other_preset(
            source_obj, presetset=target_presetset, **patch
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        presetset = PresetSet.objects.get(sodar_uuid=self.request.data["presetset"])
        return presetset.project

    def get_queryset(self):
        return QualityPresets.objects.all()


class ChromosomePresetsListCreateAjaxView(
    _ListCreateMixin,
    _PresetSetMemberMixinListCreate,
    SODARAPIGenericProjectMixin,
    ListCreateAPIView,
):
    """Create & list ``ChromosomePresets`` objects.

    **URL:** ``/variants/ajax/chromosomepresets/list-create/<uuid:presetset>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "presetset"

    schema = None
    serializer_class = ChromosomePresetsSerializer

    def get_queryset(self):
        return ChromosomePresets.objects.filter(presetset=self.get_presetset())


class ChromosomePresetsRetrieveUpdateDestroyAjaxView(
    _RetrieveUpdateDestroyMixin,
    _PresetSetMemberMixinCreateRetrieveDestroy,
    SODARAPIGenericProjectMixin,
    RetrieveUpdateDestroyAPIView,
):
    """Allow retrieval, update, destruction of ``ChromosomePreset``.

    **URL:** ``/variants/ajax/chromosomepresets/retrieve-update-destroy/<uuid:chromosomepresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "chromosomepresets"

    schema = None
    serializer_class = ChromosomePresetsSerializer

    def get_queryset(self):
        return ChromosomePresets.objects.all()


class ChromosomePresetsCloneFactoryPresetsAjaxView(
    _ListCreateMixin, SODARAPIGenericProjectMixin, CreateModelMixin, GenericAPIView
):
    """Clone factory presets.

    You must pass in a target PresetSet UUID as ``presetset``.

    **Method:** POST

    **URL:** ``/variants/ajax/chromosome/clone-factory-presets/{name}/``
    """

    schema = None
    serializer_class = ChromosomePresetsSerializer

    permission_classes = [_PresetSetMemberCloneOtherPermission]

    def post(self, request, *args, **kwargs):
        target_presetset = PresetSet.objects.get(sodar_uuid=request.data["presetset"])
        instance = ChromosomePresets.objects.create_as_copy_of_factory_preset(
            self.kwargs["name"], request.data["label"], target_presetset
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        presetset = PresetSet.objects.get(sodar_uuid=self.request.data["presetset"])
        return presetset.project

    def get_queryset(self):
        return ChromosomePresets.objects.all()


class ChromosomePresetsCloneOtherAjaxView(
    _ListCreateMixin,
    SODARAPIGenericProjectMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericAPIView,
):
    """Clone other preset set, by default in same project.

    Override target PresetSet with ``presetset``.

    **Method:** POST

    **URL:** ``/variants/ajax/chromosomepresets/clone-other/<uuid:chromosomepresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "chromosomepresets"

    schema = None
    serializer_class = ChromosomePresetsSerializer

    def post(self, request, *args, **kwargs):
        source_obj = self.get_object()
        target_presetset = source_obj.presetset
        if request.data.get("presetset"):
            target_presetset = get_object_or_404(
                PresetSet.objects.all(), sodar_uuid=request.data.get("presetset")
            )
        patch = {}
        if request.data.get("label"):
            patch["label"] = request.data.get("label")
        instance = ChromosomePresets.objects.create_as_copy_of_other_preset(
            source_obj, presetset=target_presetset, **patch
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        presetset = PresetSet.objects.get(sodar_uuid=self.request.data["presetset"])
        return presetset.project

    def get_queryset(self):
        return ChromosomePresets.objects.all()


class FlagsEtcPresetsListCreateAjaxView(
    _ListCreateMixin,
    _PresetSetMemberMixinListCreate,
    SODARAPIGenericProjectMixin,
    ListCreateAPIView,
):
    """Create & list ``FlagsEtcPresets`` objects.

    **URL:** ``/variants/ajax/flagsetcpresets/list-create/<uuid:presetset>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "presetset"

    schema = None
    serializer_class = FlagsEtcPresetsSerializer

    def get_queryset(self):
        return FlagsEtcPresets.objects.filter(presetset=self.get_presetset())


class FlagsEtcPresetsRetrieveUpdateDestroyAjaxView(
    _RetrieveUpdateDestroyMixin,
    _PresetSetMemberMixinCreateRetrieveDestroy,
    SODARAPIGenericProjectMixin,
    RetrieveUpdateDestroyAPIView,
):
    """Allow retrieval, update, destruction of ``FlagsEtcPreset``.

    **URL:** ``/variants/ajax/flagsetcpresets/retrieve-update-destroy/<uuid:flagsetcpresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "flagsetcpresets"

    schema = None
    serializer_class = FlagsEtcPresetsSerializer

    def get_queryset(self):
        return FlagsEtcPresets.objects.all()


class FlagsEtcPresetsCloneFactoryPresetsAjaxView(
    _ListCreateMixin, SODARAPIGenericProjectMixin, CreateModelMixin, GenericAPIView
):
    """Clone factory presets.

    You must pass in a target PresetSet UUID as ``presetset``.

    **Method:** POST

    **URL:** ``/variants/ajax/flagsetc/clone-factory-presets/{name}/``
    """

    schema = None
    serializer_class = FlagsEtcPresetsSerializer

    permission_classes = [_PresetSetMemberCloneOtherPermission]

    def post(self, request, *args, **kwargs):
        target_presetset = PresetSet.objects.get(sodar_uuid=request.data["presetset"])
        instance = FlagsEtcPresets.objects.create_as_copy_of_factory_preset(
            self.kwargs["name"], request.data["label"], target_presetset
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        presetset = PresetSet.objects.get(sodar_uuid=self.request.data["presetset"])
        return presetset.project

    def get_queryset(self):
        return FlagsEtcPresets.objects.all()


class FlagsEtcPresetsCloneOtherAjaxView(
    _ListCreateMixin,
    SODARAPIGenericProjectMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericAPIView,
):
    """Clone other preset set, by default in same project.

    Override target PresetSet with ``presetset``.

    **Method:** POST

    **URL:** ``/variants/ajax/flagsetcpresets/clone-other/<uuid:flagsetcpresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "flagsetcpresets"

    schema = None
    serializer_class = FlagsEtcPresetsSerializer

    def post(self, request, *args, **kwargs):
        source_obj = self.get_object()
        target_presetset = source_obj.presetset
        if request.data.get("presetset"):
            target_presetset = get_object_or_404(
                PresetSet.objects.all(), sodar_uuid=request.data.get("presetset")
            )
        patch = {}
        if request.data.get("label"):
            patch["label"] = request.data.get("label")
        instance = FlagsEtcPresets.objects.create_as_copy_of_other_preset(
            source_obj, presetset=target_presetset, **patch
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        presetset = PresetSet.objects.get(sodar_uuid=self.request.data["presetset"])
        return presetset.project

    def get_queryset(self):
        return FlagsEtcPresets.objects.all()


class QuickPresetsListCreateAjaxView(
    _ListCreateMixin,
    _PresetSetMemberMixinListCreate,
    SODARAPIGenericProjectMixin,
    ListCreateAPIView,
):
    """Create & list ``QuickPresets`` objects.

    **URL:** ``/variants/ajax/quickpresets/list-create/<uuid:presetset>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "presetset"

    schema = None
    serializer_class = QuickPresetsSerializer

    def get_queryset(self):
        return QuickPresets.objects.filter(presetset=self.get_presetset())


class QuickPresetsRetrieveUpdateDestroyAjaxView(
    _RetrieveUpdateDestroyMixin,
    _PresetSetMemberMixinCreateRetrieveDestroy,
    SODARAPIGenericProjectMixin,
    RetrieveUpdateDestroyAPIView,
):
    """Allow retrieval, update, destruction of ``QuickPreset``.

    **URL:** ``/variants/ajax/quickpresets/retrieve-update-destroy/<uuid:quickpreset>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "quickpresets"

    schema = None
    serializer_class = QuickPresetsSerializer

    def get_queryset(self):
        return QuickPresets.objects.all()


class QuickPresetsCloneOtherAjaxView(
    _ListCreateMixin,
    SODARAPIGenericProjectMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericAPIView,
):
    """Clone other quick presets.

    As the per-category presets must exist in the same preset set, must be created in the same preset set.

    **Method:** POST

    **URL:** ``/variants/ajax/quickpresets/clone-other/<uuid:quickpresets>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "quickpresets"

    schema = None
    serializer_class = QuickPresetsSerializer

    def post(self, request, *args, **kwargs):
        source_obj = self.get_object()
        patch = {}
        if request.data.get("label"):
            patch["label"] = request.data.get("label")
        instance = QuickPresets.objects.create_as_copy_of_other_preset(source_obj, **patch)
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        return QuickPresets.objects.get(sodar_uuid=self.kwargs["quickpresets"])

    def get_queryset(self):
        return QuickPresets.objects.filter(project=self.get_project())


class PresetSetListAllAjaxView(LoginRequiredMixin, ListAPIView):
    """List all ``PresetSet`` objects visible to user.

    **URL:** ``/variants/ajax/presetset/list/``.
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    schema = None
    serializer_class = PresetSetSerializer

    def get_queryset(self):
        # Note: getting all projects that the user has access to is inefficient and can be un-made so after
        # sodar-core upgrade to the upcoming v0.12.
        projects = [
            p
            for p in Project.objects.all()
            if self.request.user.has_perm("variants.view_presets", p)
        ]
        return PresetSet.objects.filter(project__in=projects).prefetch_related(
            "project",
            "quickpresets_set",
            "frequencypresets_set",
            "impactpresets_set",
            "qualitypresets_set",
            "chromosomepresets_set",
            "flagsetcpresets_set",
        )


class PresetSetListCreateAjaxView(
    _ListCreateMixin,
    SODARAPIGenericProjectMixin,
    ListCreateAPIView,
):
    """Create & list ``PresetSet``.

    **URL:** ``/variants/ajax/presetset/list-create/<uuid:project>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "project"

    schema = None
    serializer_class = PresetSetSerializer

    def get_queryset(self):
        return PresetSet.objects.filter(project=self.get_project()).prefetch_related(
            "project",
            "quickpresets_set",
            "frequencypresets_set",
            "impactpresets_set",
            "qualitypresets_set",
            "chromosomepresets_set",
            "flagsetcpresets_set",
        )


class PresetSetRetrieveUpdateDestroyAjaxView(
    _RetrieveUpdateDestroyMixin, SODARAPIGenericProjectMixin, RetrieveUpdateDestroyAPIView
):
    """Allow retrieval, update, destruction of ``PresetSet``.

    **URL:** ``/variants/ajax/presetset/retrieve-update-destroy/<uuid:presetset>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "presetset"

    schema = None
    serializer_class = PresetSetSerializer


class PresetSetCloneFactoryDefaultsPermission(SODARAPIProjectPermission):
    def get_project(self, request=None, kwargs=None):
        return Project.objects.get(sodar_uuid=request.data.get("project"))


class PresetSetCloneFactoryPresetsAjaxView(
    _ListCreateMixin, SODARAPIGenericProjectMixin, CreateModelMixin, GenericAPIView
):
    """Clone factory presets.

    You must pass in a target project UUID as ``project``.

    **Method:** POST

    **URL:** ``/variants/ajax/presetset/clone-factory-presets/``
    """

    schema = None
    serializer_class = PresetSetSerializer

    permission_classes = [PresetSetCloneFactoryDefaultsPermission]

    def post(self, request, *args, **kwargs):
        target_project = self.get_project()
        patch = {}
        if request.data.get("label"):
            patch["label"] = request.data.get("label")
        instance = PresetSet.objects.create_as_copy_of_factory_preset_set(
            project=target_project, **patch
        )
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_project(self, *args, **kwargs):
        return get_object_or_404(Project.objects.all(), sodar_uuid=self.request.data.get("project"))


class PresetSetCloneOtherAjaxView(
    _ListCreateMixin,
    SODARAPIGenericProjectMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericAPIView,
):
    """Clone other preset set, by default in same project.

    Override target project with ``project``.

    **Method:** POST

    **URL:** ``/variants/ajax/presetset/clone-other/<uuid:presetset>/``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "presetset"

    schema = None
    serializer_class = PresetSetSerializer

    def post(self, request, *args, **kwargs):
        source_obj = self.get_object()
        target_project = source_obj.project
        if request.data.get("project"):
            target_project = get_object_or_404(
                Project.objects.all(), sodar_uuid=request.data.get("project")
            )
        patch = {"project": target_project}
        if request.data.get("label"):
            patch["label"] = request.data.get("label")
        instance = PresetSet.objects.create_as_copy_of_other_preset_set(source_obj, **patch)
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectDefaultPresetSetRetrieveAjaxView(
    _RetrieveUpdateDestroyMixin, SODARAPIGenericProjectMixin, RetrieveAPIView
):
    """
    List all presets for the given category.

    **URL:** ``/variants/ajax/project-default-presetset/<uuid:project>/``

    **Methods:** ``GET``

    **Returns:** A dict mapping each of the category names to category preset values.
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "project"

    schema = None
    serializer_class = PresetSetSerializer

    def get_permission_required(self):
        return "variants.view_data"

    def get(self, *args, **kwargs):
        presetset = PresetSet.objects.filter(
            project__sodar_uuid=self.kwargs["project"], default_presetset=True
        )
        if presetset.exists():
            serializer = self.get_serializer(presetset.first())
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({})
