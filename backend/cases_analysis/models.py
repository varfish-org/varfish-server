"""Models for the ``cases_analysis`` module."""

import typing
import uuid as uuid_object

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from variants.models import Case

#: User model.
User = get_user_model()


class BaseModel(models.Model):
    """Base model with sodar_uuid and creation/update time."""

    #: UUID used in URLs.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CaseAnalysis(BaseModel):
    """Analysis of a case (at most once for now)."""

    #: The related case.
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        unique=True,  # for now
    )

    def get_absolute_url(self):
        return reverse(
            "cases_analysis:api-caseanalysis-detail",
            kwargs={"case": self.case.sodar_uuid, "caseanalysis": self.sodar_uuid},
        )

    def __str__(self):
        return f"CaseAnalysis '{self.sodar_uuid}'"


class CaseAnalysisSession(BaseModel):
    """A user session for a ``CaseAnalysis`` (at most one per user for now)."""

    #: The related ``CaseAnalysis``.
    caseanalysis = models.ForeignKey(
        CaseAnalysis,
        on_delete=models.CASCADE,
    )
    #: The related ``User``.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    @property
    def case(self) -> typing.Optional[Case]:
        try:
            return self.caseanalysis.case
        except AttributeError:
            return None

    def get_absolute_url(self):
        return reverse(
            "cases_analysis:api-caseanalysissession-detail",
            kwargs={
                "case": self.caseanalysis.case.sodar_uuid,
                "caseanalysissession": self.sodar_uuid,
            },
        )

    def __str__(self):
        return f"CaseAnalysisSession '{self.sodar_uuid}'"

    class Meta:
        # We constrain to one session per case analysis and user for now.
        unique_together = [("caseanalysis", "user")]
