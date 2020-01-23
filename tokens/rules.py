"""Permissions configured using django-rules."""

import rules


# ``tplems.access`` -- Access to the tokens app.
rules.add_perm("tokens.access", rules.is_active)
