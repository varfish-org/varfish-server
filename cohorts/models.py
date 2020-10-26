from collections import defaultdict

from django.db import models

# Create your models here.
from django.urls import reverse

from django.conf import settings
import uuid as uuid_object


#: Django user model.
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Cohort(models.Model):
    """Class for ``Cohort`` model.
    """

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Cohort UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Cohort SODAR UUID"
    )

    name = models.CharField(max_length=512)
    #: User who created the cohorts.
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_related",
        help_text="User who created the cohorts",
    )

    #: The related base project.
    project = models.ForeignKey(
        "variants.CaseAwareProject",
        null=False,
        related_name="cohorts",
        help_text="The base project of the cohorts.",
    )

    #: Cases selected by the user for this query
    cases = models.ManyToManyField("variants.Case", default=None)

    class Meta:
        ordering = ["-date_modified"]

    def get_absolute_url(self):
        return reverse("cohorts:list", kwargs={"project": self.project.sodar_uuid})

    def get_accessible_cases_for_user(self, user):
        if user == self.user or user.is_superuser:
            case_query = self.cases.all()
        else:
            case_query = self.cases.filter(project__roles__user=user)
        return case_query.order_by("name")

    def indices(self, user):
        """Return all registered indices."""
        return [p.index for p in self.get_accessible_cases_for_user(user)]

    def pedigree(self, user):
        """Concatenate the pedigrees of project's cases."""
        result = []
        seen = set()
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_accessible_cases_for_user(user):
            for line in case.pedigree:
                if line["patient"] not in seen:
                    result.append(line)
                seen.add((case.name, line["patient"]))
        return result

    def get_filtered_pedigree_with_samples(self, user):
        """Concatenate the pedigrees of project's cases that have samples."""
        result = []
        seen = set()
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_accessible_cases_for_user(user):
            for line in case.get_filtered_pedigree_with_samples():
                if line["patient"] not in seen:
                    result.append(line)
                seen.add((case.name, line["patient"]))
        return result

    def get_family_with_filtered_pedigree_with_samples(self, user):
        """Concatenate the pedigrees of project's cases that have samples."""
        result = defaultdict(list)
        seen = set()
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_accessible_cases_for_user(user):
            for line in case.get_filtered_pedigree_with_samples():
                if line["patient"] not in seen:
                    result[case.name].append(line)
                seen.add((case.name, line["patient"]))
        return dict(result)

    def get_members(self, user):
        """Return concatenated list of members in ``pedigree``."""
        return sorted([x["patient"] for x in self.get_filtered_pedigree_with_samples(user)])
