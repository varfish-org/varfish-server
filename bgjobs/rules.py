import rules
from projectroles import rules as pr_rules  # To access common predicates


# Predicates -------------------------------------------------------------------


# TODO: If we need to assign new predicates, we do it here


# Rules ------------------------------------------------------------------------


# TODO: Rules should not be needed, use permissions for user rights


# Permissions ------------------------------------------------------------------

# Allow viewing of background jobs
rules.add_perm(
    "bgjobs.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)

# Allow viewing of background jobs
rules.add_perm(
    "bgjobs.view_jobs_own",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)

# Allow creating background jobs
rules.add_perm(
    "bgjobs.create_bgjob",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)

# Allow modifying or deleting the user's background jobs
rules.add_perm(
    "bgjobs.update_bgjob_own",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)

# Allow modifying or deleting all background jobs
rules.add_perm(
    "bgjobs.update_bgjob_all",
    rules.is_superuser | pr_rules.is_project_owner | pr_rules.is_project_delegate,
)

# Allow update and deletion fo background jobs
rules.add_perm(
    "bgjobs.remove_bgjob",
    rules.is_superuser | pr_rules.is_project_owner | pr_rules.is_project_delegate,
)
