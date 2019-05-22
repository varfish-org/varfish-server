"""Factory Boy factory classes for ``bgjobs``."""

import factory
from bgjobs.models import BackgroundJob


class BackgroundJobFactory(factory.django.DjangoModelFactory):
    """Factory for ``BackgroundJobFactory`` model."""

    class Meta:
        model = BackgroundJob

    project = (
        None
    )  # Can't set this because of circular dependency. factory.SubFactory(ProjectFactory)
    user = None  # Wait for SODAR core to offer a UserFactory
    job_type = "type"
