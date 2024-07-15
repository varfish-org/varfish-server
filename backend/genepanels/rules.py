"""Rule definitions for the ``genenpanelss`` app."""

import rules

# Rules ------------------------------------------------------------------------


rules.add_perm("genepanels.view_data", rules.is_authenticated)

rules.add_perm("genepanels.add_data", rules.is_superuser)
rules.add_perm("genepanels.delete_data", rules.is_superuser)
rules.add_perm("genepanels.update_data", rules.is_superuser)
