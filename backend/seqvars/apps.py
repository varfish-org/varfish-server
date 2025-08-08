import sys

from django.apps import AppConfig


class SeqvarsConfig(AppConfig):
    name = "seqvars"

    def ready(self):
        """Hook to execute after app startup."""
        if "runserver" in sys.argv:
            self.store_factory_defaults()

    def store_factory_defaults(self):
        """Store factory defaults from in database."""
        # We must import here to avoid AppRegistryNotReady exceptions.
        from seqvars import factory_defaults  # noqa: F401

        factory_defaults.store_factory_defaults()
