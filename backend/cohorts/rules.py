from projectroles import rules as pr_rules
import rules


@rules.predicate
def is_cohort_owner(user, cohort):
    return cohort.user == user


rules.add_perm(
    "cohorts.create_cohort",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)
rules.add_perm(
    "cohorts.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)
rules.add_perm(
    "cohorts.delete_cohort",
    rules.is_superuser | is_cohort_owner,
)
rules.add_perm(
    "cohorts.update_cohort",
    rules.is_superuser | is_cohort_owner,
)
