import datetime

import factory

from cases_analysis.models import CaseAnalysis, CaseAnalysisSession
from varfish.users.tests.factories import UserFactory
from variants.tests.factories import CaseFactory


class BaseFactory(factory.django.DjangoModelFactory):
    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    class Meta:
        abstract = True


class CaseAnalysisFactory(BaseFactory):
    case = factory.SubFactory(CaseFactory)

    class Meta:
        model = CaseAnalysis
        abstract = False


class CaseAnalysisSessionFactory(BaseFactory):
    user = factory.SubFactory(UserFactory)
    caseanalysis = factory.SubFactory(CaseAnalysisFactory)

    class Meta:
        model = CaseAnalysisSession
        abstract = False
