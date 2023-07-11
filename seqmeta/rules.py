import rules

rules.add_perm("seqmeta.view_data", rules.is_authenticated)

rules.add_perm("seqmeta.update_data", rules.is_superuser)

rules.add_perm("seqmeta.delete_data", rules.is_superuser)
