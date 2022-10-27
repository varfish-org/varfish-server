"""Factory Boy factory classes for ``clinvar_export``."""

import hashlib

from django.utils import timezone
import factory

from variants.tests.factories import CaseFactory, ProjectFactory

from ..models import (
    REPORT_TYPES,
    AssertionMethod,
    ClinVarReport,
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


#: Header of the ClinVar submitter report.
CLINVAR_SUBMITTER_REPORT_HEADER = """##Report of ClinVar's processing of your recent submission
##Explanation of the columns in this report
#Your_variant_id:          the identifier you may have submitted for the reported allele
#VariantID:                the identifier assigned by ClinVar and used to build the URL, namely https://ncbi.nlm.nih.gov/clinvar/VariantID
#AlleleID:                 the list of of identifiers assigned by ClinVar to each simple allele generated from your submission
#Your_record_id:           the identifier you may have submitted for the reported allele-disorder combination
#SCV:                      the accession assigned by ClinVar to your submitted interpretation of the Variation-Condition relationship
#RCV:                      the accession assigned by ClinVar to the aggregation of your submission with other submissions of an interpretation of the same Variation-Condition relationship
#Your_variant_description  a concatenated list of the definitions you supplied of each allele in this record. This may include both HGVS expressions and a SequenceLocation report.
#Preferred_variant_name    the name ClinVar calculates for the VariantiD
#Your condition name       the name you submitted for the condition you interpreted
#Your condition identifier the identifer you submitted for the condition you intepreted
#ClinVar_condition_name    the preferred condition name in ClinVar
#Assigned_Concept_ID       the MedGen concept id for the preferred condition name in ClinVar (may be null)
#Clinical_significance     your interpretation of the variation-condition relationship
#Date_last_evaluated       your report of the last date you evaluated the variation-condition relationship
#Assertion_criteria        the name of the assertion criterion you supplied
#Submission_date           the date of your latest submission
#Novelty                   the contribution your initial submission made relative to other records in ClinVar
#Status                    the status of the SCV being reported. A comprehensive report, including status other than current, is provided only on request
#Info                      an optional set of warning about this record relative to other data at NCBI
#Invalid                   a warning that NCBI was not able to process your variant description as supplied
#
#Your_variant_id\tVariantID\tAlleleID\tYour_record_id\tSCV\tRCV\tYour_variant_description\tPreferred_variant_name\tYour_condition_name\tYour_condition_identifier\tClinVar_condition_name\tAssigned_Concept_ID\tClinical_significance\tDate_last_evaluated\tAssertion_criteria\tSubmission_date\tSubmitted_gene\tNovelty\tStatus\tInfo\tInvalid
"""


#: Header of the ClinVar error report.
CLINVAR_ERROR_REPORT_HEADER = """##Report of the submissions ClinVar could not process
##Explanation of the columns in this report
#Your VariantID :          the identifier you may have submitted for the reported allele
#RecordID:                 either the identifier you submitted for the reported allele-disorder combination or the one constructed by ClinVar to track the submission
#SubmissionStatus:         how you identified the type of submission, e.g. novel or update. Important, for example, if a submission is reported to be novel but there are already data for the same allele /disease combination in the database from you.
#Your variant definition   This may be an HGVS expression or a SequenceLocation report.
#Condition identifiers     name or database identifiers submitted for the condition you intepreted
#Info                      explanation of why this submission failed. If the term is Review, we will attach more information
#Your VariantID\tRecordID\tAccession\tSubmissionStatus\tSubmitted HGVS\tSubmitted location\tCondition identifiers\tInfo
"""


class ClinVarReportFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``ClinVarReport`` objects."""

    class Meta:
        model = ClinVarReport

    report_type = factory.Sequence(lambda n: REPORT_TYPES[n % 2])
    submission_set = factory.SubFactory(SubmissionSetFactory)
    payload = CLINVAR_SUBMITTER_REPORT_HEADER

    @factory.lazy_attribute
    def payload_md5(self):
        return hashlib.md5(self.payload.encode("utf-8")).hexdigest()
