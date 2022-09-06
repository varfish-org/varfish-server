from django.template import Context, Template

from cohorts.models import Cohort
from cohorts.tests.factories import TestCohortBase


class TestTemplateTagsCohortsTags(TestCohortBase):
    def test_get_accessible_cases_as_superuser(self):
        user = self.superuser
        cohort = self._create_cohort_all_possible_cases(user, self.project2)
        context = Context({"object_list": Cohort.objects.all(), "user": user})
        template = Template(
            "{% load cohorts_tags %}"
            "{% for item in object_list %}"
            "{{ item|get_accessible_cases:user|join:',' }}"
            "{% endfor %}"
        )
        rendered = template.render(context)
        reference = ",".join(
            [case.name for case in cohort.get_accessible_cases_for_user(user=user)]
        )
        self.assertEqual(reference, rendered)

    def test_get_accessible_cases_as_contributor(self):
        user = self.contributor
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(user, project)
        context = Context({"object_list": Cohort.objects.all(), "user": user})
        template = Template(
            "{% load cohorts_tags %}"
            "{% for item in object_list %}"
            "{{ item|get_accessible_cases:user|join:',' }}"
            "{% endfor %}"
        )
        rendered = template.render(context)
        reference = ",".join(
            [case.name for case in cohort.get_accessible_cases_for_user(user=user)]
        )
        self.assertEqual(reference, rendered)

    def test_get_accessible_cases_as_superuser_created_by_contributor(self):
        user = self.superuser
        cohort = self._create_cohort_all_possible_cases(self.contributor, self.project2)
        context = Context({"object_list": Cohort.objects.all(), "user": user})
        template = Template(
            "{% load cohorts_tags %}"
            "{% for item in object_list %}"
            "{{ item|get_accessible_cases:user|join:',' }}"
            "{% endfor %}"
        )
        rendered = template.render(context)
        reference = ",".join(
            [case.name for case in cohort.get_accessible_cases_for_user(user=user)]
        )
        self.assertEqual(reference, rendered)

    def test_get_accessible_cases_as_contributor_created_by_superuser(self):
        user = self.contributor
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(self.superuser, project)
        context = Context({"object_list": Cohort.objects.all(), "user": user})
        template = Template(
            "{% load cohorts_tags %}"
            "{% for item in object_list %}"
            "{{ item|get_accessible_cases:user|join:',' }}"
            "{% endfor %}"
        )
        rendered = template.render(context)
        reference = ",".join(
            [case.name for case in cohort.get_accessible_cases_for_user(user=user)]
        )
        self.assertEqual(reference, rendered)

    def test_check_accessible_cases_as_superuser(self):
        user = self.superuser
        self._create_cohort_all_possible_cases(user, self.project2)
        context = Context({"object_list": Cohort.objects.all(), "user": user})
        template = Template(
            "{% load cohorts_tags %}"
            "{% for item in object_list %}"
            "{% if not item|check_accessible_cases:user %}"
            "warning"
            "{% endif %}"
            "{% endfor %}"
        )
        rendered = template.render(context)
        self.assertEqual("", rendered)

    def test_check_accessible_cases_as_contributor(self):
        user = self.contributor
        project = self.project2
        self._create_cohort_all_possible_cases(user, project)
        context = Context({"object_list": Cohort.objects.all(), "user": user})
        template = Template(
            "{% load cohorts_tags %}"
            "{% for item in object_list %}"
            "{% if not item|check_accessible_cases:user %}"
            "warning"
            "{% endif %}"
            "{% endfor %}"
        )
        rendered = template.render(context)
        self.assertEqual("", rendered)

    def test_check_accessible_cases_as_superuser_created_by_contributor(self):
        user = self.superuser
        self._create_cohort_all_possible_cases(self.contributor, self.project2)
        context = Context({"object_list": Cohort.objects.all(), "user": user})
        template = Template(
            "{% load cohorts_tags %}"
            "{% for item in object_list %}"
            "{% if not item|check_accessible_cases:user %}"
            "warning"
            "{% endif %}"
            "{% endfor %}"
        )
        rendered = template.render(context)
        self.assertEqual("", rendered)

    def test_check_accessible_cases_as_contributor_created_by_superuser(self):
        user = self.contributor
        project = self.project2
        self._create_cohort_all_possible_cases(self.superuser, project)
        context = Context({"object_list": Cohort.objects.all(), "user": user})
        template = Template(
            "{% load cohorts_tags %}"
            "{% for item in object_list %}"
            "{% if not item|check_accessible_cases:user %}"
            "warning"
            "{% endif %}"
            "{% endfor %}"
        )
        rendered = template.render(context)
        self.assertEqual("warning", rendered)
