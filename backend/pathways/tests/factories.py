"""Factory Boy factory classes for ``pathways``."""

import factory

from ..models import EnsemblToKegg, KeggInfo, RefseqToKegg


class KeggInfoFactory(factory.django.DjangoModelFactory):
    """Factory for the ``KeggInfo`` model."""

    class Meta:
        model = KeggInfo

    kegg_id = factory.Sequence(lambda n: "hsa%d" % n)
    name = factory.Sequence(lambda n: "Pathway %d" % n)


class ToKeggFactoryBase(factory.django.DjangoModelFactory):
    """Base class for the models mapping gene IDs to KEGG pathways."""

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to get rid of the ``kegginfo`` keyword argument and instead define ``kegginfo_id``."""
        manager = cls._get_manager(model_class)
        kegginfo = kwargs.pop("kegginfo")
        kwargs["kegginfo_id"] = kegginfo.id
        return manager.create(*args, **kwargs)

    #: Model pseudo-attribute, not stored in database.  Instead, ``case_id`` is stored.
    kegginfo = factory.SubFactory(KeggInfoFactory)
    #: The actual reference to the KeggInfo.
    kegginfo_id = factory.LazyAttribute(lambda o: o.kegginfo.kegg_id)


class EnsemblToKeggFactory(ToKeggFactoryBase):
    """Factory for the ``EnsemblToKegg`` model."""

    @classmethod
    def _create(cls, *args, **kwargs):
        return super()._create(*args, **kwargs)

    class Meta:
        model = EnsemblToKegg


class RefseqToKeggFactory(ToKeggFactoryBase):
    """Factory for the ``Mim2geneMedgen`` model."""

    @classmethod
    def _create(cls, *args, **kwargs):
        return super()._create(*args, **kwargs)

    class Meta:
        model = RefseqToKegg
