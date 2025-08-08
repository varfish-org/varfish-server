import factory
from projectroles.forms import PROJECT_ROLE_CONTRIBUTOR, PROJECT_ROLE_OWNER
from projectroles.models import Role
from projectroles.tests.test_models import RoleAssignmentMixin, RoleMixin
from test_plus import TestCase

from cohorts.models import Cohort, CohortCase
from variants.models import Case
from variants.tests.factories import (
    CaseFactory,
    CaseWithVariantSetFactory,
    ProjectFactory,
    SmallVariantFactory,
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


class TestCohortBase(RoleAssignmentMixin, RoleMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

        # Provided by RoleMixin
        self.init_roles()

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
        self.make_assignment(self.project1, owner, role_owner)
        self.make_assignment(self.project2, owner, role_owner)

        # contributor gets access to project2
        self.make_assignment(self.project2, self.contributor, role_contributor)

    def _create_cohort_all_possible_cases(self, user, project):
        cases = Case.objects.all()
        if not user.is_superuser:
            cases = [c for c in cases if c.project.has_role(user)]
        return CohortFactory.create(user=user, project=project, cases=cases)


class CohortCaseFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``cohorts`` ``CohortCase`` objects."""

    class Meta:
        model = CohortCase

    cohort = factory.SubFactory(CohortFactory)
    case = factory.SubFactory(CaseFactory)
