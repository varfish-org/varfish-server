from django.contrib.messages import get_messages
from django.urls import reverse

from cohorts.models import Cohort
from cohorts.tests.factories import TestCohortBase
from variants.models import Case


class TestCohortView(TestCohortBase):
    def test_list_view_empty_as_superuser(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse("cohorts:list", kwargs={"project": self.project1.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)

    def test_list_view_empty_as_contributor(self):
        with self.login(self.contributor):
            response = self.client.get(
                reverse("cohorts:list", kwargs={"project": self.project2.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)

    def test_list_view_as_superuser_two_cohorts_from_each_all_cases(self):
        project = self.project2
        cohort_superuser = self._create_cohort_all_possible_cases(self.superuser, project)
        cohort_contributor = self._create_cohort_all_possible_cases(self.contributor, project)
        all_cases = Case.objects.all()
        contributor_cases = Case.objects.filter(project__roles__user=self.contributor)
        with self.login(self.superuser):
            response = self.client.get(
                reverse("cohorts:list", kwargs={"project": project.sodar_uuid})
            )
            self.assertEqual(response.context["object_list"][0].name, cohort_contributor.name)
            self.assertEqual(
                set(response.context["object_list"][0].cases.all()), set(contributor_cases)
            )
            self.assertEqual(response.context["object_list"][1].name, cohort_superuser.name)
            self.assertEqual(set(response.context["object_list"][1].cases.all()), set(all_cases))

    def test_list_view_as_contributor_two_cohorts_from_each_all_cases(self):
        project = self.project2
        user = self.contributor
        cohort_superuser = self._create_cohort_all_possible_cases(self.superuser, project)
        cohort_contributor = self._create_cohort_all_possible_cases(user, project)
        contributor_cases = Case.objects.filter(project__roles__user=user)
        with self.login(user):
            response = self.client.get(
                reverse("cohorts:list", kwargs={"project": project.sodar_uuid})
            )
            self.assertEqual(response.context["object_list"][0].name, cohort_contributor.name)
            self.assertEqual(
                set(response.context["object_list"][0].get_accessible_cases_for_user(user)),
                set(contributor_cases),
            )
            self.assertEqual(response.context["object_list"][1].name, cohort_superuser.name)
            self.assertEqual(
                set(response.context["object_list"][1].get_accessible_cases_for_user(user)),
                set(contributor_cases),
            )

    def test_list_view_as_superuser_two_cohorts_from_each_check_displayed_buttons(self):
        project = self.project2
        user = self.superuser
        cohort_superuser = self._create_cohort_all_possible_cases(user, project)
        cohort_contributor = self._create_cohort_all_possible_cases(self.contributor, project)
        with self.login(user):
            response = self.client.get(
                reverse("cohorts:list", kwargs={"project": project.sodar_uuid})
            )
            self.assertContains(
                response,
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort_superuser.sodar_uuid},
                ),
            )
            self.assertContains(
                response,
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort_superuser.sodar_uuid},
                ),
            )
            self.assertContains(
                response,
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort_contributor.sodar_uuid},
                ),
            )
            self.assertContains(
                response,
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort_contributor.sodar_uuid},
                ),
            )

    def test_list_view_as_contributor_two_cohorts_from_each_check_displayed_buttons(self):
        project = self.project2
        user = self.contributor
        cohort_superuser = self._create_cohort_all_possible_cases(self.superuser, project)
        cohort_contributor = self._create_cohort_all_possible_cases(user, project)
        with self.login(user):
            response = self.client.get(
                reverse("cohorts:list", kwargs={"project": project.sodar_uuid})
            )
            self.assertNotContains(
                response,
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort_superuser.sodar_uuid},
                ),
            )
            self.assertNotContains(
                response,
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort_superuser.sodar_uuid},
                ),
            )
            self.assertContains(
                response,
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort_contributor.sodar_uuid},
                ),
            )
            self.assertContains(
                response,
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort_contributor.sodar_uuid},
                ),
            )


class TestCohortCreateView(TestCohortBase):
    def test_cohort_create_render_form_as_superuser(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse("cohorts:create", kwargs={"project": self.project1.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)
            self.assertListEqual(list(response.context["projects"]), [self.project1, self.project2])

    def test_cohort_create_render_form_as_contributor(self):
        with self.login(self.contributor):
            response = self.client.get(
                reverse("cohorts:create", kwargs={"project": self.project2.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)
            self.assertListEqual(list(response.context["projects"]), [self.project2])

    def test_cohort_create_submit_form_as_superuser_project1_all_possible_cases(self):
        user = self.superuser
        project = self.project1
        all_cases = [case.id for case in Case.objects.all()]
        form_data = {
            "name": "TestCohort",
            "cases": all_cases,
        }
        with self.login(user):
            response = self.client.post(
                reverse("cohorts:create", kwargs={"project": project.sodar_uuid}),
                form_data,
            )
            self.assertRedirects(
                response,
                reverse(
                    "cohorts:list",
                    kwargs={"project": project.sodar_uuid},
                ),
            )
            self.assertEqual(Cohort.objects.count(), 1)
            cohort = Cohort.objects.first()
            cohort_cases = [case.id for case in cohort.cases.all()]
            self.assertEqual(cohort.name, form_data["name"])
            self.assertEqual(set(form_data["cases"]), set(cohort_cases))
            self.assertEqual(set(all_cases), set(cohort_cases))

    def test_cohort_create_submit_form_as_superuser_project2_all_possible_cases(self):
        user = self.superuser
        project = self.project2
        all_cases = [case.id for case in Case.objects.all()]
        form_data = {
            "name": "TestCohort",
            "cases": all_cases,
        }
        with self.login(user):
            self.client.post(
                reverse("cohorts:create", kwargs={"project": project.sodar_uuid}),
                form_data,
            )
            self.assertEqual(Cohort.objects.count(), 1)
            cohort = Cohort.objects.first()
            cohort_cases = [case.id for case in cohort.cases.all()]
            self.assertEqual(cohort.name, form_data["name"])
            self.assertEqual(set(form_data["cases"]), set(cohort_cases))
            self.assertEqual(set(all_cases), set(cohort_cases))

    def test_cohort_create_submit_form_as_contributor_project2_all_possible_cases(self):
        user = self.contributor
        project = self.project2
        all_cases = [case.id for case in Case.objects.all()]
        form_data = {
            "name": "TestCohort",
            "cases": [case.id for case in Case.objects.filter(project__roles__user=user)],
        }
        with self.login(user):
            self.client.post(
                reverse("cohorts:create", kwargs={"project": project.sodar_uuid}),
                form_data,
            ),
            self.assertEqual(Cohort.objects.count(), 1)
            cohort = Cohort.objects.first()
            cohort_cases = [case.id for case in cohort.cases.all()]
            self.assertEqual(set(form_data["cases"]), set(cohort_cases))
            self.assertNotEqual(set(all_cases), set(cohort_cases))


class TestCohortUpdateView(TestCohortBase):
    def test_cohort_update_render_form_as_superuser(self):
        """
        Selection is tested in test_form.py
        """
        user = self.superuser
        project = self.project1
        cohort = self._create_cohort_all_possible_cases(user, project)
        with self.login(user):
            response = self.client.get(
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["form"].initial["name"], cohort.name)
            self.assertEqual(
                set(response.context["form"].initial["cases"]),
                set(cohort.get_accessible_cases_for_user(user)),
            )
            self.assertListEqual(list(response.context["projects"]), [self.project1, self.project2])

    def test_cohort_update_render_form_as_contributor(self):
        """
        Selection is tested in test_form.py
        """
        user = self.contributor
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(user, project)
        with self.login(user):
            response = self.client.get(
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["form"].initial["name"], cohort.name)
            self.assertEqual(
                set(response.context["form"].initial["cases"]),
                set(cohort.get_accessible_cases_for_user(user)),
            )
            self.assertListEqual(list(response.context["projects"]), [self.project2])

    def test_cohort_update_submit_form_as_superuser(self):
        user = self.superuser
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(user, project)
        self.assertEqual(Cohort.objects.count(), 1)
        form_data = {
            "name": "TestCohort Altered",
            "cases": [self.project1_case1.id, self.project2_case2.id],
        }
        with self.login(user):
            response = self.client.post(
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
                form_data,
            )
            self.assertRedirects(
                response,
                reverse(
                    "cohorts:list",
                    kwargs={"project": project.sodar_uuid},
                ),
            )
            self.assertEqual(Cohort.objects.count(), 1)
            cohort_altered = Cohort.objects.first()
            messages = [m.message for m in get_messages(response.wsgi_request)]
            self.assertEqual(
                "Cohort <strong>%s</strong> updated." % cohort_altered.name, messages[0]
            )
            self.assertEqual(form_data["name"], cohort_altered.name)
            self.assertEqual(
                set(form_data["cases"]),
                set([case.id for case in cohort_altered.get_accessible_cases_for_user(user)]),
            )

    def test_cohort_update_submit_form_as_contributor(self):
        user = self.contributor
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(user, project)
        self.assertEqual(Cohort.objects.count(), 1)
        form_data = {
            "name": "TestCohort Altered",
            "cases": [self.project2_case1.id],
        }
        with self.login(user):
            response = self.client.post(
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
                form_data,
            )
            self.assertRedirects(
                response,
                reverse(
                    "cohorts:list",
                    kwargs={"project": project.sodar_uuid},
                ),
            )
            self.assertEqual(Cohort.objects.count(), 1)
            cohort_altered = Cohort.objects.first()
            messages = [m.message for m in get_messages(response.wsgi_request)]
            self.assertEqual(
                "Cohort <strong>%s</strong> updated." % cohort_altered.name, messages[0]
            )
            self.assertEqual(form_data["name"], cohort_altered.name)
            self.assertEqual(
                set(form_data["cases"]),
                set([case.id for case in cohort_altered.get_accessible_cases_for_user(user)]),
            )

    def test_cohort_update_render_form_as_superuser_for_cohort_by_contributor(self):
        """
        Selection is tested in test_form.py
        """
        user = self.superuser
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(self.contributor, project)
        with self.login(user):
            response = self.client.get(
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["form"].initial["name"], cohort.name)
            self.assertEqual(
                set(response.context["form"].initial["cases"]),
                set(cohort.get_accessible_cases_for_user(user)),
            )

    def test_cohort_update_render_form_as_contributor_for_cohort_by_superuser(self):
        """
        Selection is tested in test_form.py
        """
        user = self.contributor
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(self.superuser, project)
        with self.login(user):
            response = self.client.get(
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["form"].initial["name"], cohort.name)
            # This is somehow problematic. The modified queryset for the form doesn't apply here.
            # Anyway, this case shouldn't be possible anyway.
            # self.assertEqual(
            #     set(response.context["form"].initial["cases"]),
            #     set(cohort.get_accessible_cases_for_user(user)),
            # )

    def test_cohort_update_submit_form_as_superuser_for_cohort_by_contributor(self):
        user = self.superuser
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(self.contributor, project)
        self.assertEqual(Cohort.objects.count(), 1)
        form_data = {
            "name": "TestCohort Altered",
            "cases": [self.project1_case1.id, self.project2_case2.id],
        }
        with self.login(user):
            response = self.client.post(
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
                form_data,
            )
            self.assertRedirects(
                response,
                reverse(
                    "cohorts:list",
                    kwargs={"project": project.sodar_uuid},
                ),
            )
            self.assertEqual(Cohort.objects.count(), 1)
            cohort_altered = Cohort.objects.first()
            messages = [m.message for m in get_messages(response.wsgi_request)]
            self.assertEqual(
                "Cohort <strong>%s</strong> updated." % cohort_altered.name, messages[0]
            )
            self.assertEqual(form_data["name"], cohort_altered.name)
            self.assertEqual(
                set(form_data["cases"]),
                set([case.id for case in cohort_altered.get_accessible_cases_for_user(user)]),
            )

    def test_cohort_update_submit_form_as_contributor_for_cohort_by_superuser(self):
        user = self.contributor
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(self.superuser, project)
        self.assertEqual(Cohort.objects.count(), 1)
        form_data = {
            "name": "TestCohort Altered",
            "cases": [self.project2_case1.id],
        }
        with self.login(user):
            response = self.client.post(
                reverse(
                    "cohorts:update",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
                form_data,
            )
            self.assertRedirects(
                response,
                reverse(
                    "cohorts:list",
                    kwargs={"project": project.sodar_uuid},
                ),
            )
            messages = [m.message for m in get_messages(response.wsgi_request)]
            self.assertEqual("Can't update other user's cohort.", messages[0])
            self.assertEqual(Cohort.objects.count(), 1)
            cohort_altered = Cohort.objects.first()
            self.assertEqual(cohort_altered.name, cohort.name)


class TestCohortDeleteView(TestCohortBase):
    def test_cohort_delete_render_form_as_superuser(self):
        user = self.superuser
        project = self.project1
        cohort = self._create_cohort_all_possible_cases(user, project)
        with self.login(user):
            response = self.client.get(
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["object"], cohort)
            self.assertEqual(set(response.context["object"].cases.all()), set(cohort.cases.all()))

    def test_cohort_delete_render_form_as_contributor(self):
        user = self.contributor
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(user, project)
        with self.login(user):
            response = self.client.get(
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["object"], cohort)
            self.assertEqual(set(response.context["object"].cases.all()), set(cohort.cases.all()))

    def test_cohort_delete_submit_delete_as_superuser(self):
        user = self.superuser
        project = self.project1
        cohort = self._create_cohort_all_possible_cases(user, project)
        self.assertEqual(Cohort.objects.count(), 1)
        with self.login(user):
            response = self.client.post(
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
            )
            self.assertRedirects(
                response,
                reverse(
                    "cohorts:list",
                    kwargs={"project": project.sodar_uuid},
                ),
            )
        self.assertEqual(Cohort.objects.count(), 0)

    def test_cohort_delete_submit_delete_as_contributor(self):
        user = self.contributor
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(user, project)
        self.assertEqual(Cohort.objects.count(), 1)
        with self.login(user):
            response = self.client.post(
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
            )
            self.assertRedirects(
                response,
                reverse(
                    "cohorts:list",
                    kwargs={"project": project.sodar_uuid},
                ),
            )
        self.assertEqual(Cohort.objects.count(), 0)

    def test_cohort_delete_render_form_as_superuser_for_cohort_by_contributor(self):
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(self.contributor, project)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["object"], cohort)
            self.assertEqual(set(response.context["object"].cases.all()), set(cohort.cases.all()))

    def test_cohort_delete_render_form_as_contributor_for_cohort_by_superuser(self):
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(self.superuser, project)
        with self.login(self.contributor):
            response = self.client.get(
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["object"], cohort)
            self.assertNotEqual(
                set(response.context["object"].get_accessible_cases_for_user(self.contributor)),
                set(cohort.cases.all()),
            )

    def test_cohort_delete_submit_delete_as_superuser_for_cohort_by_contributor(self):
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(self.contributor, project)
        self.assertEqual(Cohort.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
            )
            self.assertRedirects(
                response,
                reverse(
                    "cohorts:list",
                    kwargs={"project": project.sodar_uuid},
                ),
            )
            messages = [m.message for m in get_messages(response.wsgi_request)]
            self.assertEqual("Cohort <strong>%s</strong> deleted." % cohort.name, messages[0])
            self.assertEqual(Cohort.objects.count(), 0)

    def test_cohort_delete_submit_delete_as_contributor_for_cohort_by_superuser(self):
        project = self.project2
        cohort = self._create_cohort_all_possible_cases(self.superuser, project)
        self.assertEqual(Cohort.objects.count(), 1)
        with self.login(self.contributor):
            response = self.client.post(
                reverse(
                    "cohorts:delete",
                    kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
                ),
            )
            self.assertRedirects(
                response,
                reverse(
                    "cohorts:list",
                    kwargs={"project": project.sodar_uuid},
                ),
            )
            messages = [m.message for m in get_messages(response.wsgi_request)]
            self.assertEqual("Can't delete other user's cohort.", messages[0])
            self.assertEqual(Cohort.objects.count(), 1)
