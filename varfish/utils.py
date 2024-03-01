"""Shared utility code."""

import json
from typing import Callable, List, Tuple

import django.db.models.fields.json

from varfish.users.models import User


def get_subclasses(classes, level=0):
    """Return the list of all subclasses given class (or list of classes) has.

    Also see https://stackoverflow.com/q/3862310/84349.
    """
    if not isinstance(classes, list):
        classes = [classes]

    if level < len(classes):
        classes += classes[level].__subclasses__()
        return get_subclasses(classes, level + 1)
    else:
        return classes


def receiver_subclasses(signal, sender, dispatch_uid_prefix, **kwargs):
    """A decorator for connecting receivers and all receiver's subclasses to signals.

    Used by passing in the signal and keyword arguments to connect::

        @receiver_subclasses(post_save, sender=MyModel)
        def signal_receiver(sender, **kwargs):
            ...
    """

    def _decorator(func):
        all_senders = get_subclasses(sender)
        for snd in all_senders:
            signal.connect(
                func, sender=snd, dispatch_uid=dispatch_uid_prefix + "_" + snd.__name__, **kwargs
            )
        return func

    return _decorator


class JSONField(django.db.models.fields.json.JSONField):
    """Helper JSONField class that works when SQLAlchemy (via aldjemy) is already parsing JSON values into Python types."""

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # Some backends (SQLite at least) extract non-string values in their
        # SQL datatypes.
        if isinstance(expression, django.db.models.fields.json.KeyTransform) and not isinstance(
            value, str
        ):
            return value
        try:
            return json.loads(value, cls=self.decoder)
        except (json.JSONDecodeError, TypeError):
            return value


# Monkey-patch original JSON field as we cannot control models outside of our app.
django.db.models.fields.json.JSONField.from_db_value = JSONField.from_db_value


class VarFishKioskUserMiddleware:
    """Automatically assigns the ``kiosk_user`` to ``request.user``."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = User.get_kiosk_user()
        response = self.get_response(request)
        return response


def spectacular_preprocess_hook(endpoints: List[Tuple[str, str, str, Callable]]) -> List[Tuple[str, str, str, Callable]]:
    """Ignore some endpoints."""
    # URL prefixes to ignore from django-sodar-core
    ignore_prefixes = [
        # knox
        "/api/auth/",
        # django-sodar-core
        "/admin_alerts/ajax/",
        "/app_alerts/ajax/",
        "/timeline/ajax/",
        "/project/ajax/",
        # local, but skipped for now
        "/beaconsite/",
    ]

    result = []
    for (path, path_regex, method, callback) in endpoints:
        if not any(path.startswith(prefix) for prefix in ignore_prefixes):
            result.append((
                path, path_regex, method, callback
            ))
    return result
