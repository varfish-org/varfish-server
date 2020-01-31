"""Shared utility code."""

from projectroles.views import ProjectAccessMixin


class ApiProjectAccessMixin(ProjectAccessMixin):
    """Project access mixing for DRF API view classes."""

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project(request=result["request"])
        return result


class ProjectAccessSerializerMixin:
    """Mixin that automatically sets the project fields of objects."""

    def update(self, instance, validated_data):
        validated_data["project"] = self.context["project"]
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)


# class SODARAPIBaseView(APIView):
#     """Base SODAR API View with accept header versioning"""
#
#     versioning_class = SODARAPIVersioning
#     renderer_classes = [SODARAPIRenderer]


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
