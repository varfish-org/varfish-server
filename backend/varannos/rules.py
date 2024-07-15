from projectroles import rules as pr_rules
import rules

rules.add_perm(
    "varannos.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)

rules.add_perm("varannos.add_data", rules.is_superuser)

rules.add_perm("varannos.update_data", rules.is_superuser)
