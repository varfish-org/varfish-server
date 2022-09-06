"""Factory Boy factory classes for ``clinvar_export``."""

from django.utils import timezone
import factory

from variants.tests.factories import CaseFactory, ProjectFactory

from ..models import (
    AssertionMethod,
    Family,
    Individual,
    Organisation,
    Submission,
    SubmissionIndividual,
    SubmissionSet,
    Submitter,
    SubmittingOrg,
)


class FamilyFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Family`` objects."""

    class Meta:
        model = Family

    project = factory.LazyAttribute(lambda o: o.case.project)
    case = factory.SubFactory(CaseFactory)
    case_name = factory.SelfAttribute("case.name")


class IndividualFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Individual`` objects."""

    class Meta:
        model = Individual

    family = factory.SubFactory(FamilyFactory)
    name = factory.LazyAttribute(lambda o: o.family.case.pedigree[0]["patient"])
    sex = factory.sequence(lambda n: ("male", "female", "unknown")[n % 2])
    affected = "yes"


class AssertionMethodFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``AssertionMethod`` objects."""

    class Meta:
        model = AssertionMethod

    is_builtin = False
    title = factory.Sequence(lambda n: "Assertion Method #%d" % n)
    reference = factory.sequence(lambda n: "PMID:1%03d" % n)


class SubmitterFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Submitter`` objects."""

    class Meta:
        model = Submitter

    clinvar_id = factory.Sequence(lambda n: 1000 + n)
    name = factory.Sequence(lambda n: "Submitter #%d" % n)


class OrganisationFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Organisation`` objects."""

    class Meta:
        model = Organisation

    clinvar_id = factory.Sequence(lambda n: 1000 + n)
    name = factory.Sequence(lambda n: "Organisation #%d" % n)


class SubmissionSetFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``SubmissionSet`` objects."""

    class Meta:
        model = SubmissionSet

    project = factory.SubFactory(ProjectFactory)
    state = factory.Sequence(lambda n: ["pending", "submitted", "released", "rejected"][n % 4])
    title = factory.Sequence(lambda n: "Submission #%d" % n)
    submitter = factory.SubFactory(SubmitterFactory)


class SubmissionFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Submission`` objects."""

    class Meta:
        model = Submission

    age_of_onset = "Antenatal"
    variant_type = "Variation"
    inheritance = "Other"
    submission_set = factory.SubFactory(SubmissionSetFactory)
    sort_order = factory.Sequence(lambda n: n)
    significance_status = "criteria provided, single submitter"
    significance_description = "Pathogenic"
    significance_last_evaluation = factory.LazyAttribute(lambda _: timezone.now())
    assertion_method = factory.SubFactory(AssertionMethodFactory)
    variant_assembly = "GRCh37"
    variant_chromosome = factory.Sequence(lambda n: str((n % 22) + 1))
    variant_start = factory.Sequence(lambda n: 1_000_000 + n)
    variant_stop = factory.Sequence(lambda n: 1_000_000 + n)
    variant_reference = factory.Sequence(lambda n: "ACGT"[n % 4])
    variant_alternative = factory.Sequence(lambda n: "GTAC"[n % 4])
    variant_gene = factory.Sequence(lambda n: ["GENE%d" % n])
    variant_hgvs = factory.Sequence(lambda n: ["p.W%dU" % (n + 1)])
    diseases = factory.Sequence(
        lambda n: [{"term_id": "OMIM:%07d" % n, "term_name": "Disease %d" % n}]
    )


class SubmittingOrgFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``SubmittingOrg`` objects."""

    class Meta:
        model = SubmittingOrg

    sort_order = factory.Sequence(lambda n: n)
    organisation = factory.SubFactory(OrganisationFactory)
    submission_set = factory.SubFactory(SubmissionSetFactory)


class SubmissionIndividualFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``SubmissionIndividual`` objects."""

    class Meta:
        model = SubmissionIndividual

    sort_order = factory.Sequence(lambda n: n)
    phenotypes = factory.Sequence(
        lambda n: [{"term_id": "HP:%07d" % n, "term_name": "Term #%d" % n}]
    )
    submission = factory.SubFactory(SubmissionFactory)
    individual = factory.SubFactory(IndividualFactory)

    source = factory.Sequence(lambda n: ("clinical testing", "research", "not provided")[n % 3])
    citations = factory.List([])
    tissue = factory.sequence(lambda n: ("blood", "saliva")[n % 2])
    variant_origin = "germline"
    variant_allele_count = 1
    variant_zygosity = "Homozygote"


class SubmissionWithIndividualFactory(SubmissionFactory):
    related_individual_first = factory.RelatedFactory(
        SubmissionIndividualFactory, factory_related_name="submission"
    )
    related_individual_second = factory.RelatedFactory(
        SubmissionIndividualFactory, factory_related_name="submission"
    )


class SubmissionSetWithOrgFactory(SubmissionSetFactory):
    related_org_primary = factory.RelatedFactory(
        SubmittingOrgFactory, factory_related_name="submission_set"
    )
    related_org_secondary = factory.RelatedFactory(
        SubmittingOrgFactory, factory_related_name="submission_set"
    )


class SubmissionSetWithRelatedsFactory(SubmissionSetFactory):
    related_org_primary = factory.RelatedFactory(
        SubmittingOrgFactory, factory_related_name="submission_set"
    )
    related_org_secondary = factory.RelatedFactory(
        SubmittingOrgFactory, factory_related_name="submission_set"
    )
    submission_first = factory.RelatedFactory(
        SubmissionWithIndividualFactory, factory_related_name="submission_set"
    )
    submission_second = factory.RelatedFactory(
        SubmissionWithIndividualFactory, factory_related_name="submission_set"
    )
