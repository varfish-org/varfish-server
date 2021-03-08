"""Rule definitions for the ``beaconsites`` app."""

import rules
from projectroles import rules as pr_rules


# Rules ------------------------------------------------------------------------


rules.add_perm("beaconsite.view_data", rules.is_superuser)

rules.add_perm("beaconsite.add_data", rules.is_superuser)
rules.add_perm("beaconsite.delete_data", rules.is_superuser)
rules.add_perm("beaconsite.update_data", rules.is_superuser)
