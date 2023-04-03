from projectroles import rules as pr_rules
import rules


@rules.predicate
def is_casecomment_author(user, casecomment):
    return casecomment.user.pk == user.pk


@rules.predicate
def is_casecomment_project_owner(user, casecomment):
    return pr_rules.is_project_delegate(user, casecomment.case.project)


@rules.predicate
def is_casecomment_project_delegate(user, casecomment):
    return pr_rules.is_project_owner(user, casecomment.case.project)


@rules.predicate
def is_casecomment_project_contributor(user, casecomment):
    return pr_rules.is_project_contributor(user, casecomment.case.project)


@rules.predicate
def is_casecomment_project_guest(user, casecomment):
    return pr_rules.is_project_guest(user, casecomment.case.project)


rules.add_perm(
    "cases.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)

rules.add_perm(
    "cases.add_case",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)
rules.add_perm("cases.delete_case", rules.is_superuser)
rules.add_perm(
    "cases.update_case",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)
rules.add_perm(
    "cases.sync_remote",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)

# This rule refers to a project that the case comment is to be created in.
rules.add_perm(
    "cases.casecomment_create",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)
# The rules below apply to casecomments and not projects as above.
rules.add_perm(
    "cases.casecomment_view",
    rules.is_superuser
    | is_casecomment_project_owner
    | is_casecomment_project_delegate
    | is_casecomment_project_contributor
    | is_casecomment_project_guest,
)
rules.add_perm("cases.casecomment_delete", rules.is_superuser | is_casecomment_author)
rules.add_perm("cases.casecomment_update", rules.is_superuser | is_casecomment_author)
