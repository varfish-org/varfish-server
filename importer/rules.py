"""Rule definitions for the ``bgjobs`` app."""

from projectroles import rules as pr_rules
import rules

# Predicates -------------------------------------------------------------------


# TODO: If we need to assign new predicates, we do it here


# Rules ------------------------------------------------------------------------

is_allowed_to_modify = (
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
)

rules.add_perm(
    "importer.view_import",
    is_allowed_to_modify,
)

rules.add_perm("importer.add_import", is_allowed_to_modify)
rules.add_perm("importer.delete_import", is_allowed_to_modify)
rules.add_perm("importer.update_import", is_allowed_to_modify)

# Permissions ------------------------------------------------------------------

# Allow viewing of import release info
rules.add_perm("importer.view_data", rules.is_authenticated)
