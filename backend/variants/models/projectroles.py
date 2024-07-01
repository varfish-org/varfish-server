"""Code for adapting with ``projectroles``."""

from collections import defaultdict

from projectroles.app_settings import AppSettingAPI
from projectroles.models import Project

from variants.models.variants import SmallVariantSet

_app_settings = AppSettingAPI()


class CaseAwareProject(Project):
    """A project that is aware of its cases"""

    class Meta:
        proxy = True

    def indices(self, _user=None):
        """Return all registered indices."""
        return [p.index for p in self.get_active_smallvariant_cases()]

    def pedigree(self, _user=None):
        """Concatenate the pedigrees of project's cases."""
        result = []
        seen = set()
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_active_smallvariant_cases():
            for line in case.pedigree:
                if line["patient"] not in seen:
                    result.append(line)
                seen.add((case.name, line["patient"]))
        return result

    def get_filtered_pedigree_with_samples(self, _user=None):
        """Concatenate the pedigrees of project's cases that have samples."""
        result = []
        seen = set()
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_active_smallvariant_cases():
            for line in case.get_filtered_pedigree_with_samples():
                if line["patient"] not in seen:
                    result.append(line)
                seen.add((case.name, line["patient"]))
        return result

    def get_family_with_filtered_pedigree_with_samples(self, _user=None):
        """Concatenate the pedigrees of project's cases that have samples."""
        result = defaultdict(list)
        seen = set()
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_active_smallvariant_cases():
            for line in case.get_filtered_pedigree_with_samples():
                if line["patient"] not in seen:
                    result[case.name].append(line)
                seen.add((case.name, line["patient"]))
        return dict(result)

    def sample_to_case(self):
        """Compute sample-to-case mapping."""
        result = {}
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_active_smallvariant_cases():
            for line in case.pedigree:
                if line["patient"] not in result:
                    result[line["patient"]] = case
        return result

    def chrx_het_hom_ratio(self, sample):
        """Forward to appropriate case"""
        case = self.sample_to_case().get(sample)
        if not case:
            return 0.0
        else:
            return case.chrx_het_hom_ratio(sample)

    def sex_errors(self) -> dict[str, list[str]]:
        """Concatenate all contained case's sex errors dicts"""
        result = {}
        disable_sex_check = _app_settings.get(
            "variants", "disable_pedigree_sex_check__project", project=self
        )
        if disable_sex_check:
            return result
        for case in self.case_set.all():
            result.update(case.sex_errors(disable_sex_check))
        return result

    def sex_errors_to_fix(self):
        for case in self.case_set.all():
            fix_case = case.sex_errors_variant_stats(lambda x: x)
            if fix_case:
                return True
        return False

    def get_case_pks(self):
        """Return PKs for cases."""
        return [case.pk for case in self.case_set.all()]

    def get_members(self):
        """Return concatenated list of members in ``pedigree``."""
        return sorted([x["patient"] for x in self.get_filtered_pedigree_with_samples()])

    def get_active_smallvariant_cases(self):
        """Return activate cases."""
        return list(self.case_set.filter(smallvariantset__state="active"))

    def num_small_vars(self):
        """Return total number of small vars in a project."""
        return sum(
            case.num_small_vars for case in self.case_set.all() if case.num_small_vars is not None
        )

    def has_variants_and_variant_sets(self):
        return all(case.has_variants_and_variant_set() for case in self.case_set.all())

    def casealignmentstats(self):
        stats = []
        for case in self.case_set.all():
            variant_set = case.latest_variant_set
            if variant_set:
                stats.append(variant_set.casealignmentstats)
        return stats

    def get_annotation_count(self):
        return sum(case.get_annotation_count() for case in self.case_set.all())

    def sample_variant_stats(self):
        stats = []
        for case in self.case_set.all():
            variant_set = case.latest_variant_set
            if variant_set:
                try:
                    for sample in variant_set.variant_stats.sample_variant_stats.all():
                        stats.append(sample)
                except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
                    pass
        return stats
