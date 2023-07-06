from projectroles import rules as pr_rules
import rules

rules.add_perm(
    "variants.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)
rules.add_perm(
    "variants.update_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
)
rules.add_perm(
    "variants.delete_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
)

rules.add_perm(
    "variants.add_case",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)
rules.add_perm("variants.delete_case", rules.is_superuser)
rules.add_perm(
    "variants.update_case",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)
rules.add_perm(
    "variants.sync_remote",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)

can_view_presets = (
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest
)
can_update_presets = (
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
)
rules.add_perm("variants.view_presets", can_view_presets)
rules.add_perm("variants.add_presets", can_update_presets)
rules.add_perm("variants.update_presets", can_update_presets)
rules.add_perm("variants.delete_presets", can_update_presets)
