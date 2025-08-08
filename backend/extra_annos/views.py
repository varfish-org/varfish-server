import typing

from .models import AugmentedExtraAnno, ExtraAnno, ExtraAnnoField


# TODO clean up
class ExtraAnnosMixin:
    """Mixin for returing variant extra arguments."""

    def get_extra_annos(self, query_kwargs) -> typing.Optional[AugmentedExtraAnno]:
        """Given a variant, return the corresponding variant frequencies."""
        fields = list(ExtraAnnoField.objects.all())
        annos = ExtraAnno.objects.filter(
            release=query_kwargs["release"],
            chromosome=query_kwargs["chromosome"],
            start=query_kwargs["start"],
            end=query_kwargs["end"],
            reference=query_kwargs["reference"],
            alternative=query_kwargs["alternative"],
        )
        return AugmentedExtraAnno.create(annos.first(), fields) if annos else None

    def get_extra_annos_api(self, query_kwargs):
        """Given a variant, return the corresponding variant frequencies."""
        annos = ExtraAnno.objects.filter(
            release=query_kwargs["release"],
            chromosome=query_kwargs["chromosome"],
            start=query_kwargs["start"],
            end=query_kwargs["end"],
            reference=query_kwargs["reference"],
            alternative=query_kwargs["alternative"],
        )
        return annos.first() if annos else None
