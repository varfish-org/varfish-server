from cohorts.tests.factories import CohortFactory, TestCohortBase


class TestTemplateTagsCohortsTags(TestCohortBase):
    def test_get_accessible_cases_as_superuser_created_by_contributor(self):
        cases = [
            self.project2_case1,
            self.project2_case2,
        ]
        cohort = CohortFactory.create(user=self.contributor, project=self.project2, cases=cases)
        self.assertEqual(set(cases), set(cohort.get_accessible_cases_for_user(user=self.superuser)))

    def test_get_accessible_cases_as_contributor_created_by_superuser(self):
        cases = [
            self.project1_case1,
            self.project1_case2,
            self.project2_case1,
            self.project2_case2,
        ]
        cohort = CohortFactory.create(user=self.superuser, project=self.project2, cases=cases)
        self.assertEqual(
            set(cases[2:4]), set(cohort.get_accessible_cases_for_user(user=self.contributor))
        )
