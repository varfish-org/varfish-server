import factory
from projectroles.forms import PROJECT_ROLE_OWNER, PROJECT_ROLE_CONTRIBUTOR
from projectroles.models import Role
from projectroles.tests.test_models import RoleAssignmentMixin
from test_plus import TestCase

from cohorts.models import Cohort
from variants.models import Case
from variants.tests.factories import (
    ProjectFactory,
    SmallVariantFactory,
    CaseWithVariantSetFactory,
)


class CohortFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``cohorts`` ``Cohort`` objects."""

    class Meta:
        model = Cohort

    user = None
    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: "TestCohort%s" % n)

    @factory.post_generation
    def cases(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for case in extracted:
                self.cases.add(case)


class TestCohortBase(RoleAssignmentMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

        # setup users

        # setup super user
        self.superuser = self.make_user("superuser")
        self.superuser.is_staff = True
        self.superuser.is_superuser = True
        self.superuser.save()

        # setup contributor user
        self.contributor = self.make_user("contributor")

        # setup owner for projects, not used in tests
        owner = self.make_user("owner")

        # setup cases & projects & roles

        # project 1 case 1
        self.project1 = ProjectFactory()
        self.project1_case1, variant_set_1, _ = CaseWithVariantSetFactory.get(
            "small", project=self.project1
        )
        self.project1_case1_smallvars = SmallVariantFactory.create_batch(
            1, variant_set=variant_set_1
        )

        # project 1 case 2
        self.project1_case2, variant_set_2, _ = CaseWithVariantSetFactory.get(
            "small", project=self.project1
        )
        self.project1_case2_smallvars = SmallVariantFactory.create_batch(
            2, variant_set=variant_set_2
        )
        # project 2 case 1
        self.project2 = ProjectFactory()
        self.project2_case1, variant_set_3, _ = CaseWithVariantSetFactory.get(
            "small", project=self.project2
        )
        self.project2_case1_smallvars = SmallVariantFactory.create_batch(
            4, variant_set=variant_set_3
        )

        # project 2 case 2
        self.project2_case2, variant_set_4, _ = CaseWithVariantSetFactory.get(
            "small", project=self.project2
        )
        self.project2_case2_smallvars = SmallVariantFactory.create_batch(
            8, variant_set=variant_set_4
        )

        # init roles
        role_owner = Role.objects.get_or_create(name=PROJECT_ROLE_OWNER)[0]
        role_contributor = Role.objects.get_or_create(name=PROJECT_ROLE_CONTRIBUTOR)[0]

        # owner owns project1 and project2 (all projects)
        self._make_assignment(self.project1, owner, role_owner)
        self._make_assignment(self.project2, owner, role_owner)
        # contributor gets access to project2
        self._make_assignment(self.project2, self.contributor, role_contributor)

    def _create_cohort_all_possible_cases(self, user, project):
        if user.is_superuser:
            cases = Case.objects.all()
        else:
            cases = Case.objects.filter(project__roles__user=user)
        return CohortFactory.create(user=user, project=project, cases=cases)
