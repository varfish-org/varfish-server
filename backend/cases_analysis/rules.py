from projectroles import rules as pr_rules
import rules

rules.add_perm(
    "cases_analysis.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)
