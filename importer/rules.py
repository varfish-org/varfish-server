"""Rule definitions for the ``bgjobs`` app."""

import rules
from projectroles import rules as pr_rules


# Predicates -------------------------------------------------------------------


# TODO: If we need to assign new predicates, we do it here


# Rules ------------------------------------------------------------------------


rules.add_perm(
    "importer.view_import",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)

rules.add_perm("importer.add_import", rules.is_superuser | pr_rules.is_project_contributor)
rules.add_perm("importer.delete_import", rules.is_superuser)
rules.add_perm("importer.update_import", rules.is_superuser | pr_rules.is_project_contributor)

# Permissions ------------------------------------------------------------------

# Allow viewing of import release info
rules.add_perm("importer.view_data", rules.is_authenticated)
