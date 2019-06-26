import binning
import factory

from annotation.models import Annotation


class AnnotationFactory(factory.django.DjangoModelFactory):
    """Factory for ``Annotation`` model."""

    class Meta:
        model = Annotation

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.SelfAttribute("start")
    bin = 0
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    database = "refseq"  # or "ensembl"
    effect = []
    gene_id = factory.LazyAttributeSequence(
        lambda o, n: str(n) if o.database == "refseq" else "ENSG%d" % n
    )
    transcript_id = factory.LazyAttributeSequence(
        lambda o, n: "NR_%d" % n if o.database == "refseq" else "ENST%d" % n
    )
    transcript_coding = False
    hgvs_c = "c.123C>T"
    hgvs_p = "p.I2T"

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()
