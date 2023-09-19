import datetime

import factory
import yaml

from cases.tests.factories import CaseFactory
from cases_qc.models import CaseQc, FragmentLengthHistogram


class CaseQcFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CaseQc

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    case = factory.SubFactory(CaseFactory)


class FragmentLengthHistogramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FragmentLengthHistogram

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    case_qc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.case_qc.case.pedigree[0]["patient"]

    keys = [37, 40, 41]
    values = [1, 100, 101]
