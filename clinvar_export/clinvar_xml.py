import datetime

from lxml import etree as ET
from lxml.builder import ElementMaker

#: URL of the XSD file
XSD_URL_1_6 = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xsd_submission/clinvar_submission_1.6.xsd"


class SubmissionXmlGenerator:
    """Helper class to create ClinVar submission XML."""

    def __init__(self):
        self.em = ElementMaker(nsmap={"xsi": "http://www.w3.org/2001/XMLSchema-instance",})

    def generate_tree(self, submission_set):
        root = self.em(
            "ClinvarSubmissionSet",
            {
                "Date": datetime.date.today().isoformat(),
                "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation": XSD_URL_1_6,
            },
        )
        root.append(
            ET.Comment(
                " Submitter & Global Information ================================================== "
            )
        )
        for tag in self.submitter_of_record(submission_set):
            root.append(tag)
        for i, submitting_org in enumerate(submission_set.submitting_orgs.all()):
            for element in self.org_id(submitting_org.organisation, i == 0):
                root.append(element)
        root.append(self.em("Title", str(submission_set.sodar_uuid)))
        root.append(
            ET.Comment(
                " Submissions ===================================================================== "
            )
        )
        for i, submission in enumerate(submission_set.submissions.all()):
            root.append(ET.Comment(" Submission %d " % (i + 1)))
            root.append(self.build_submission_tag(submission))
        return root

    def generate_str(self, submission_set):
        root = self.generate_tree(submission_set)
        return ET.tostring(root, pretty_print=True)

    def submitter_of_record(self, submission_set):
        if submission_set.submitter:
            return [
                ET.Comment(" submitter name: %s " % submission_set.submitter.name),
                self.em("SubmitterOfRecordID", str(submission_set.submitter.clinvar_id)),
            ]
        else:
            return []

    def org_id(self, organisation, is_primary):
        return [
            ET.Comment(" organisation name: %s" % organisation.name),
            self.em(
                "OrgID",
                str(organisation.clinvar_id),
                **{"Type": "primary" if is_primary else "secondary"},
            ),
        ]

    def build_submission_tag(self, submission):
        return self.em(
            "ClinvarSubmission",
            self.em("RecordStatus", submission.record_status),
            self.em("ReleaseStatus", submission.release_status),
            self.em(
                "ClinvarSubmissionID",
                **{
                    "localKey": str(submission.sodar_uuid),
                    "localKeyIsSubmitted": "1",
                    "submittedAssembly": "GRCh37",
                    "submitterDate": datetime.date.today().isoformat(),
                },
            ),
            self.build_measure_trait(submission),
            self.build_variant_measure_set(submission),
            self.build_disease_trait_set(submission),
        )

    def build_measure_trait(self, submission):
        return self.em(
            "MeasureTrait",
            self.em(
                "Assertion",
                self.em("AssertionType", "variation to disease", **{"val_type": "name"}),
            ),
            self.em(
                "ClinicalSignificance",
                self.em("ReviewStatus", submission.significance_status),
                self.em("Description", submission.significance_description),
                self.em("DateLastEvaluated", submission.significance_last_evaluation.isoformat()),
            ),
            *self.build_assertion_method_tag(submission),
            *self.build_mode_of_inheritance_tag(submission),
            *self.build_age_of_onset_tag(submission),
            *self.build_observed_in_tag(submission),
        )

    def build_assertion_method_tag(self, submission):
        if submission.assertion_method:
            assertion_method_tag = [
                self.em(
                    "AttributeSet",
                    self.em("MeasureTraitAttributeType", "AssertionMethod", **{"val_type": "name"}),
                    self.em("Attribute", submission.assertion_method.title,),
                    self.em("Citation", self.build_assertion_method_citation_child(submission)),
                )
            ]
        else:
            assertion_method_tag = []
        return assertion_method_tag

    def build_assertion_method_citation_child(self, submission):
        if submission.assertion_method.reference.startswith("PMID:"):
            return self.em(
                "ID", submission.assertion_method.reference.split(":", 1)[1], **{"Source": "PubMed"}
            )
        else:
            return self.em("URL", submission.assertion_method.reference)

    def build_mode_of_inheritance_tag(self, submission):
        if submission.inheritance:
            return [
                self.em(
                    "AttributeSet",
                    self.em(
                        "MeasureTraitAttributeType", "ModeOfInheritance", **{"val_type": "name"}
                    ),
                    self.em("Attribute", submission.inheritance),
                )
            ]
        else:
            return []

    def build_age_of_onset_tag(self, submission):
        if submission.age_of_onset:
            return [
                self.em(
                    "AttributeSet",
                    self.em("MeasureTraitAttributeType", "AgeOfOnset", **{"val_type": "name"}),
                    self.em("Attribute", submission.age_of_onset),
                )
            ]
        else:
            return []

    def build_observed_in_tag(self, submission):
        return [
            self.em(
                "ObservedIn",
                self.em(
                    "Sample",
                    self.em("Origin", "germline"),
                    *self.build_tissue(sub_ind),
                    self.em("Species", "human", **{"TaxonomyId": "9606"}),
                    self.em("AffectedStatus", sub_ind.individual.affected),
                    self.em("NumberTested", "1"),
                    self.em("Gender", sub_ind.individual.sex),
                    self.em(
                        "FamilyData", **{"PedigreeID": str(sub_ind.individual.family.sodar_uuid)}
                    ),
                    *[self.build_citation(citation) for citation in sub_ind.citations],
                ),
                self.em("Method", self.em("MethodType", sub_ind.source, **{"val_type": "name"},),),
                *self.build_variant_alleles(sub_ind),
                self.em(
                    "ObservedData",
                    self.em("ObsAttributeType", "SampleLocalID", **{"val_type": "name"}),
                    self.em("Attribute", str(sub_ind.individual.sodar_uuid)),
                ),
                *self.build_phenotype_trait_set(sub_ind),
            )
            for sub_ind in submission.submission_individuals.all()
        ]

    def build_tissue(self, individual):
        if individual.tissue:
            return [self.em("Tissue", individual.tissue)]
        else:
            return []

    def build_citation(self, citation):
        if citation.startswith("PMID:"):
            return self.em(
                "Citation", self.em("ID", citation.split(":", 1)[1], **{"Source": "PubMed"})
            )
        else:
            return self.em("Invalid-Citation", citation)

    def build_phenotype_trait_set(self, submission_individual):
        def build_xref(term_id):
            if term_id.startswith("HP:"):
                self.em("XRef", **{"db": "HP", "id": term_id,}),
            elif term_id.startswith("OMIM:") or term_id.startswith("MIM:"):
                self.em("XRef", **{"db": "OMIM", "id": ("MIM:%s" % term_id.split(":", 1)[1]),}),
            elif term_id.startswith("ORPHA:"):
                self.em(
                    "XRef", **{"db": "Orphanet", "id": ("ORPHA:%s" % term_id.split(":", 1)[1]),}
                ),
            else:
                return self.em("Invalid-XRef", term_id)

        if not submission_individual.phenotypes:
            return []
        else:
            return [
                self.em(
                    "TraitSet",
                    self.em("TraitSetType", "Finding", **{"val_type": "name"}),
                    *[
                        self.em(
                            "Trait",
                            self.em("TraitType", "Finding", **{"val_type": "name"}),
                            self.em(
                                "Name",
                                self.em("ElementValueType", "Preferred", **{"val_type": "name"}),
                                self.em("ElementValue", phenotype["term_name"]),
                            ),
                            self.em("XRef", **{"db": "HP", "id": phenotype["term_id"],}),
                        )
                        for phenotype in submission_individual.phenotypes
                    ],
                )
            ]

    def build_variant_alleles(self, sub_ind):
        result = []
        if sub_ind.variant_allele_count:
            tags = []
            if sub_ind.variant_allele_count:
                tags.append(
                    self.em("Attribute", **{"integerValue": str(sub_ind.variant_allele_count)})
                )
            if sub_ind.variant_zygosity:
                tags.append(self.em("Zygosity", sub_ind.variant_zygosity))
            result.append(
                self.em(
                    "ObservedData",
                    self.em("ObsAttributeType", "VariantAlleles", **{"val_type": "name"}),
                    *tags,
                )
            )
        return result

    def build_variant_measure_set(self, submission):
        seq_location_dict = {
            "Assembly": submission.variant_assembly,
            "Chr": submission.variant_chromosome,
            "start": str(submission.variant_start),
            "stop": str(submission.variant_stop),
        }
        if submission.variant_type in ("Deletion", "Duplication"):
            seq_location_dict["variantLength"] = str(
                submission.variant_stop - submission.variant_start + 1
            )
        else:
            if submission.variant_reference:
                seq_location_dict["referenceAllele"] = submission.variant_reference
            if submission.variant_reference:
                seq_location_dict["alternateAllele"] = submission.variant_alternative
        return self.em(
            "MeasureSet",
            self.em("MeasureSetType", "Variant", **{"val_type": "name"},),
            self.em(
                "Measure",
                self.em("MeasureType", submission.variant_type, **{"val_type": "name"}),
                self.em("SequenceLocation", **seq_location_dict,),
                self.em(
                    "MeasureRelationship",
                    self.em("MeasureRelationshipType", "variant in gene", **{"val_type": "name"},),
                    *[
                        self.em(
                            "Symbol",
                            ET.Comment(" HGVS: %s:%s " % (gene_symbol, gene_hgvs)),
                            self.em("ElementValueType", "Preferred", **{"val_type": "name"},),
                            self.em("ElementValue", gene_symbol),
                        )
                        for (gene_symbol, gene_hgvs) in zip(
                            submission.variant_gene, submission.variant_hgvs
                        )
                    ],
                ),
            ),
        )

    def build_disease_trait_set(self, submission):
        if not submission.diseases:
            traits = [
                self.em(
                    "Trait",
                    self.em("TraitType", "Disease", **{"val_type": "name"}),
                    self.em(
                        "Name",
                        self.em("ElementValueType", "Preferred", **{"val_type": "name"}),
                        self.em("ElementValue", "not specified"),
                    ),
                )
            ]
        else:
            traits = [
                self.em(
                    "Trait",
                    self.em("TraitType", "Disease", **{"val_type": "name"}),
                    ET.Comment(" (%s) %s " % (disease["term_id"], disease["term_name"])),
                    self.build_disease_xref(disease["term_id"]),
                )
                for disease in submission.diseases
            ]

        return self.em(
            "TraitSet", self.em("TraitSetType", "Disease", **{"val_type": "name"},), *traits
        )

    def build_disease_xref(self, term_id):
        if term_id.startswith("OMIM:"):
            return self.em("XRef", **{"db": "OMIM", "id": term_id.replace("OMIM:", "")})
        elif term_id.startswith("ORPHA:"):
            return self.em("XRef", **{"db": "Orphanet", "id": term_id})
        else:
            return self.em("Invalid-XRef", **{"db": "UNKNOWN", "id": term_id})
