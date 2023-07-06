"""AJAX views for detailing with SV query presets."""

import typing

import attrs
import cattr
from rest_framework import views
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from svs import query_presets
from svs.query_presets import (
    CHROMOSOME_PRESETS,
    FREQUENCY_PRESETS,
    GENOTYPE_CRITERIA_DEFINITIONS,
    IMPACT_PRESETS,
    KNOWN_PATHO_PRESETS,
    QUICK_PRESETS,
    REGULATORY_PRESETS,
    SVTYPE_PRESETS,
    TAD_PRESETS,
    Inheritance,
)
from svs.serializers import SettingsShortcuts, SvQuerySettingsShortcutsSerializer
from svs.views.ajax.queries import SvQueryListCreateAjaxViewPermission
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models import Case
from variants.views.api import CaseApiMixin


class SvCategoryPresetsApiView(
    views.APIView,
):
    """
    List all presets for the given category.

    **URL:** ``/variants/api/query-case/category-presets/{category}``

    **Methods:** ``GET``

    **Returns:** A dict mapping each of the category names to category preset values.
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get(self, *args, **kwargs):
        presets = {
            "known_patho": KNOWN_PATHO_PRESETS,
            "frequency": FREQUENCY_PRESETS,
            "impact": IMPACT_PRESETS,
            "sv_type": SVTYPE_PRESETS,
            "chromosomes": CHROMOSOME_PRESETS,
            "regulatory": REGULATORY_PRESETS,
            "tad": TAD_PRESETS,
            "genotype_criteria": GENOTYPE_CRITERIA_DEFINITIONS,
        }
        return Response(cattr.unstructure(presets.get(self.kwargs.get("category"))))


class SvInheritancePresetsApiView(
    views.APIView,
):
    """
    List all inheritance presets for the given case.

    **URL:** ``/variants/api/query-case/inheritance-presets/{case.sodar_uuid}``

    **Methods:** ``GET``

    **Returns:** A dict mapping each of the category names to category preset values.
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get(self, *args, **kwargs):
        pedigree_members = self._get_pedigree_members()
        return Response(
            {
                inheritance.value: inheritance.to_settings(pedigree_members)
                for inheritance in Inheritance
                if inheritance.value != "custom"
            }
        )

    def _get_pedigree_members(self) -> typing.Tuple[query_presets.PedigreeMember]:
        """Return pedigree members for the queried case."""
        case = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return tuple(
            query_presets.PedigreeMember(
                family=None,
                name=entry["patient"],
                father=entry["father"],
                mother=entry["mother"],
                sex=query_presets.Sex(entry["sex"]),
                disease_state=query_presets.DiseaseState(entry["affected"]),
            )
            for entry in case.pedigree
        )


class SvQuickPresetsAjaxView(
    views.APIView,
):
    """
    Resolve quick preset name to category preset.

    **URL:** ``/variants/api/query-case/quick-presets``

    **Methods:** ``GET``

    **Returns:** A dict mapping each of the category names to category preset values.
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get(self, *args, **kwargs):
        return Response(cattr.unstructure(QUICK_PRESETS))


class SvQuerySettingsShortcutAjaxView(CaseApiMixin, RetrieveAPIView):
    """AJAX endpoint to generate SV query settings for a given case by certain shortcuts.

    **URL:** ``/svs/ajax/query-case/query-settings-shortcut/{case.uuid}/``

    **Methods:** ``GET``

    **Parameters:**

    - ``quick_preset`` - overall preset selection using the presets below, valid values are

         - ``defaults`` - applies presets that are recommended for starting out without a specific hypothesis
         - ``de_novo`` - applies presets that are recommended for starting out when the hypothesis is dominannt
           inheritance with *de novo* variants
         - ``dominant`` - applies presets that are recommended for starting out when the hypothesis is dominant
           inheritance (but not with *de novo* variants)
         - ``homozygous_recessive`` - applies presets that are recommended for starting out when the hypothesis is
           recessive with homzygous variants
         - ``heterozygous_recessive`` - applies presets that are recommended for starting out when the hypothesis is
           recessive with compound heterozygous variants; will only query for SINGLE variants
         - ``x_recessive`` - applies presets that are recommended for starting out when the hypothesis is X recessive
           mode of inheritance
         - ``clinvar_pathogenic`` - apply presets that are recommended for screening variants for known pathogenic
           variants present Clinvar
         - ``mitochondrial`` - apply presets recommended for starting out to filter for mitochondrial mode of
           inheritance
         - ``whole_genome`` - apply presets that return all variants of the case, regardless of frequency, quality etc.

    - ``inheritance`` - preset selection for mode of inheritance, valid values are

        - ``any`` - no particular constraint on inheritance (default)
        - ``de_novo`` - allow variants compatible with de novo mode of inheritance
        - ``dominant`` - allow variants compatible with dominant mode of inheritance (includes *de novo* variants)
        - ``homozygous_recessive`` - allow variants compatible with homozygous recessive mode of inheritance
        - ``heterozygous_heterozygous`` - allow variants compatible with compound heterozygous recessive mode of
          inheritance
        - ``x_recessive`` - allow variants compatible with X_recessive mode of inheritance of a disease/trait
        - ``mitochondrial`` - mitochondrial inheritance (also applicable for "clinvar pathogenic")
        - ``custom`` - indicates custom settings such that none of the above inheritance settings applies

    - ``frequency`` - preset selection for frequencies, valid values are

        - ``any`` - do not apply any thresholds
        - ``strict`` - apply thresholds considered "strict"
        - ``relaxed`` - apply thresholds considered "relaxed"
        - ``custom`` - indicates custom settings such that none of the above frequency settings applies

    - ``impact`` - preset selection for molecular impact values, valid values are

        - ``any`` - allow any impact
        - ``almost_all`` - remove variants that commonly are artifacts
        - ``cnv_only`` - keep only copy number variable variants
        - ``custom`` - indicates custom settings such that none of the above impact settings applies

    - ``chromosomes`` - preset selection for selecting chromosomes/regions/genes allow/block lists, valid values are

        - ``whole_genome`` - the defaults settings selecting the whole genome
        - ``autosomes`` - select the variants lying on the autosomes only
        - ``x_chromosome`` - select variants on the X chromosome only
        - ``y_chromosome`` - select variants on the Y chromosome only
        - ``mt_chromosome`` - select variants on the mitochondrial chromosome only
        - ``custom`` - indicates custom settings such that none of the above chromosomes presets applies

    - ``regulatory`` - preset selection for regulatory feature annotation

        - ``default`` - the defaults setting selection

    - ``tad`` - preset selection for TAD feature annotation

        - ``default`` - the defaults setting

    - ``known_patho`` - presets related to known pathogenic variants and ClinVar

        - ``default`` - default settings
        - ``custom`` - indicates custom settings such that none of the above presets applies

    - ``genotype_criteria`` - selection of filter criteria

        - ``svish_high`` - "high convidence" filter criteria
        - ``svish_pass`` - "pass" filter criteria
        - ``default`` - define default filter criteria
        - ``none`` - define no filter criteria

    - ``database`` - the database to query, one of ``"refseq"`` (default) and ``"ensembl"``

    **Returns:**

    - ``presets`` - a ``dict`` with the following keys; this mirrors back the quick presets and further presets
      selected in the parameters

        - ``quick_presets`` - one of the ``quick_presets`` preset values from above
        - ``inheritance`` - one of the ``inheritance`` preset values from above
        - ``frequency`` - one of the ``frequency`` preset values from above
        - ``impact`` - one of the ``impact`` preset values from above
        - ``chromosomes`` - one of the ``chromosomes`` preset values from above
        - ``regulatory`` - feature annotation based on regulatory features, from above
        - ``tad`` - feature annotation based on TADs, from above
        - ``filter_criteria_definition`` - definition of filter criteria, from above

    - ``query_settings`` - a ``dict`` with the query settings ready to be used for the given case
    """

    serializer_class = SvQuerySettingsShortcutsSerializer

    permission_classes = [SvQueryListCreateAjaxViewPermission]

    def get_permission_required(self):
        return "svs.view_data"

    def get_object(self, *args, **kwargs):
        def value_to_enum(enum, value):
            for enum_val in enum:
                if enum_val.value == value:
                    return enum_val
            else:
                return None

        quick_preset = self._get_quick_presets()
        fields_dict = attrs.fields_dict(query_presets.QuickPresets)
        changes_raw = {
            key: self.request.query_params[key]
            for key in fields_dict
            if key in self.request.query_params
        }
        if "database" in changes_raw:
            changes = {"database": changes_raw.pop("database")}
        else:
            changes = {}
        changes.update(
            {key: value_to_enum(fields_dict[key].type, value) for key, value in changes_raw.items()}
        )
        quick_preset = attrs.evolve(quick_preset, **changes)
        presets = {}
        for key in fields_dict:
            if key == "label":
                presets[key] = getattr(quick_preset, key)
            else:
                presets[key] = getattr(quick_preset, key).value
        return SettingsShortcuts(
            presets=presets,
            query_settings=cattr.unstructure(
                quick_preset.to_settings(self._get_pedigree_members())
            ),
        )

    def _get_quick_presets(self) -> query_presets.QuickPresets:
        """Return quick preset if given in request.query_params"""
        if "quick_preset" in self.request.query_params:
            qp_name = self.request.query_params["quick_preset"]
            if qp_name not in attrs.fields_dict(query_presets._QuickPresetList):
                raise NotFound(f"Could not find quick preset {qp_name}")
            return getattr(query_presets.QUICK_PRESETS, qp_name)
        else:
            return query_presets.QUICK_PRESETS.defaults

    def _get_pedigree_members(self) -> typing.Tuple[query_presets.PedigreeMember]:
        """Return pedigree members for the queried case."""
        case = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return tuple(
            query_presets.PedigreeMember(
                family=None,
                name=entry["patient"],
                father=entry["father"],
                mother=entry["mother"],
                sex=query_presets.Sex(entry["sex"]),
                disease_state=query_presets.DiseaseState(entry["affected"]),
            )
            for entry in case.pedigree
        )
