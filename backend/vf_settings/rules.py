from projectroles import rules as pr_rules
import rules

rules.add_perm("vf_settings.view_site", rules.is_authenticated)

rules.add_perm("vf_settings.update_site", rules.is_superuser)

rules.add_perm(
    "vf_settings.view_project",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)

rules.add_perm(
    "vf_settings.update_project",
    rules.is_superuser | pr_rules.is_project_owner | pr_rules.is_project_delegate,
)

rules.add_perm(
    "vf_settings.view_project_user",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)

rules.add_perm(
    "vf_settings.update_project_user",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)

rules.add_perm("vf_settings.view_user", rules.is_authenticated)

rules.add_perm("vf_settings.update_user", rules.is_authenticated)
