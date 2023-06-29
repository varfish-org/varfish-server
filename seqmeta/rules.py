from projectroles import rules as pr_rules
import rules

rules.add_perm("seqmeta.update_data", rules.is_superuser)

rules.add_perm("seqmeta.delete_data", rules.is_superuser)

rules.add_perm(
    "seqmeta.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)
