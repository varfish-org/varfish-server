from projectroles import rules as pr_rules
import rules

rules.add_perm("settings.site.view_data", rules.is_active)

rules.add_perm("settings.site.update_data", rules.is_superuser)

rules.add_perm(
    "settings.project.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)

rules.add_perm(
    "settings.project.update_data",
    rules.is_superuser | pr_rules.is_project_owner | pr_rules.is_project_delegate,
)

rules.add_perm(
    "settings.project_user.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)

rules.add_perm(
    "settings.project_user.update_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)

rules.add_perm("settings.user.view_data", rules.is_active)

rules.add_perm("settings.user.update_data", rules.is_active)
