import datetime
import json

from bgjobs.tests.factories import BackgroundJobFactory
import factory
import yaml

from cases_import.models import CaseImportAction, CaseImportBackgroundJob
from seqmeta.tests.test_views_api import isoformat
from variants.tests.factories import ProjectFactory


class CaseImportActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CaseImportAction

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    action = CaseImportAction.ACTION_CREATE
    state = CaseImportAction.STATE_DRAFT

    @factory.lazy_attribute
    def payload(self):
        with open("cases_import/tests/data/family.yaml") as inputf:
            return yaml.safe_load(inputf)["family"]

    project = factory.SubFactory(ProjectFactory)


def case_import_action_json(**kwargs):
    """Create payload for a new ``CaseImportAction``."""
    data = factory.build(dict, FACTORY_CLASS=CaseImportActionFactory, **kwargs)
    data.pop("sodar_uuid")
    data.pop("project")
    data["date_created"] = isoformat(data["date_created"])
    data["date_modified"] = isoformat(data["date_modified"])
    return data


class CaseImportBackgroundJobFactory(factory.django.DjangoModelFactory):
    """Factory for ``ImportCaseBackgroundJob``.

    Note that the dummy argument ``user`` to pass to subfactory ``BackgroundJobFactory``.
    """

    class Meta:
        model = CaseImportBackgroundJob
        exclude = ["user"]

    user = None

    project = factory.SubFactory(ProjectFactory)
    bg_job = factory.SubFactory(
        BackgroundJobFactory,
        project=factory.SelfAttribute("factory_parent.project"),
        user=factory.SelfAttribute("factory_parent.user"),
    )

    caseimportaction = factory.SubFactory(CaseImportActionFactory)
