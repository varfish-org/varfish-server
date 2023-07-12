import datetime
import json

import factory

from cases_import.models import CaseImportAction
from seqmeta.tests.test_views_api import isoformat
from variants.tests.factories import ProjectFactory


class CaseImportActionFactory(factory.django.DjangoModelFactory):

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    action = CaseImportAction.ACTION_CREATE
    state = CaseImportAction.STATE_DRAFT

    @factory.lazy_attribute
    def payload(self):
        with open("cases_import/tests/data/zaphod.phenopacket.json") as inputf:
            return json.load(inputf)

    project = factory.SubFactory(ProjectFactory)

    class Meta:
        model = CaseImportAction


def case_import_action_json(**kwargs):
    """Create payload for a new ``CaseImportAction``."""
    data = factory.build(dict, FACTORY_CLASS=CaseImportActionFactory, **kwargs)
    data.pop("sodar_uuid")
    data.pop("project")
    data["date_created"] = isoformat(data["date_created"])
    data["date_modified"] = isoformat(data["date_modified"])
    return data
