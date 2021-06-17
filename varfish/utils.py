"""Shared utility code."""

import json

import django.db.models.fields.json


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
    """ A decorator for connecting receivers and all receiver's subclasses to signals.

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
    """Helper JSONField class that works when SQLAlchemy (via aldjemy) is already parsing JSON values into Python types.
    """

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
