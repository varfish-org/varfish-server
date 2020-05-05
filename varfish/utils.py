"""Shared utility code."""


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
