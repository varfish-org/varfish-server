"""Rule definitions for the ``bgjobs`` app."""

import rules


# Predicates -------------------------------------------------------------------


# TODO: If we need to assign new predicates, we do it here


# Rules ------------------------------------------------------------------------


# TODO: Rules should not be needed, use permissions for user rights


# Permissions ------------------------------------------------------------------

# Allow viewing of import release info
rules.add_perm("importer.view_data", rules.is_authenticated)
