from cohorts.forms import CohortForm
from cohorts.tests.factories import TestCohortBase
from variants.models import Case


class TestFilterForm(TestCohortBase):
    """Tests for FilterForm."""

    def test_submit_as_superuser(self):
        user = self.superuser
        form_data = {
            "name": "TestCohort",
            "cases": [case.id for case in Case.objects.all()],
        }
        form = CohortForm(form_data, user=user)
        self.assertTrue(form.is_valid())

    def test_submit_as_contributor(self):
        user = self.contributor
        form_data = {
            "name": "TestCohort",
            "cases": [case.id for case in Case.objects.filter(project__roles__user=user)],
        }
        form = CohortForm(form_data, user=user)
        self.assertTrue(form.is_valid())
