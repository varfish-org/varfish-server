import rules
from projectroles import rules as pr_rules

rules.add_perm(
    'varfish.main.view_data',
    rules.is_superuser | pr_rules.is_project_owner |
    pr_rules.is_project_delegate | pr_rules.is_project_contributor |
    pr_rules.is_project_guest)
