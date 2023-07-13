"""Support for the protocolbuffers in ``cases_import``."""

import typing

from phenopackets import Family, File, MetaData, Pedigree, Phenopacket, Resource, Sex


class ValidationWarning(UserWarning):
    """Warning class for warnings during validation of a ``Family``."""


class MetaDataValidationWarning(ValidationWarning):
    """Warning class used during validation of ``MetaData``."""


class PhenopacketValidationWarning(ValidationWarning):
    """Warning class used during validation of ``Phenopacket``"""


class ProbandValidationWarning(PhenopacketValidationWarning):
    """Warning class used during validation of ``Phenopacket`` as proband."""


class MetaDataValidator:
    """Helper class that allows to validate phenopackets ``MetaData``."""

    def __init__(self, metadata: MetaData):
        #: The metadata to validate
        self.metadata = metadata

    def validate(self) -> typing.List[ValidationWarning]:
        result = []
        if not self.metadata.created or self.metadata.created.seconds == 0:
            result.append(MetaDataValidationWarning("Missing /metadata/created"))
        if not self.metadata.created_by:
            result.append(MetaDataValidationWarning("Missing /metadata/created_by"))

        if not self.metadata.resources:
            result.append(MetaDataValidationWarning("Missing /metadata/resources"))
        else:
            for i, resource in enumerate(self.metadata.resources):
                result += self._validate_resource(i, resource)

        if not self.metadata.phenopacket_schema_version:
            result.append(MetaDataValidationWarning("Missing /metadata/phenopacket_schema_version"))
        else:
            tokens = self.metadata.phenopacket_schema_version.split(".")
            if tokens[0] != "2":
                result.append(
                    MetaDataValidationWarning(
                        "Unsupported /metadata/phenopacket_schema_version. "
                        f"Expected 2.* got {self.metadata.phenopacket_schema_version}."
                    )
                )
        return result

    def _validate_resource(
        self, no: int, resource: Resource
    ) -> typing.List[MetaDataValidationWarning]:
        result = []
        if not resource.id:
            result.append(MetaDataValidationWarning(f"Missing /metadata/resources/{no}/id"))
        if not resource.name:
            result.append(MetaDataValidationWarning(f"Missing /metadata/resources/{no}/name"))
        if not resource.namespace_prefix:
            result.append(
                MetaDataValidationWarning(f"Missing /metadata/resources/{no}/namespace_prefix")
            )
        if not resource.url:
            result.append(MetaDataValidationWarning(f"Missing /metadata/resources/{no}/url"))
        if not resource.version:
            result.append(MetaDataValidationWarning(f"Missing /metadata/resources/{no}/version"))
        if not resource.iri_prefix:
            result.append(MetaDataValidationWarning(f"Missing /metadata/resources/{no}/iri_prefix"))
        return result


class PhenopacketValidator:
    """Helper class that allows to validate ``Phenopacket``s"""

    def __init__(self, phenopacket: Phenopacket):
        #: The phenopacket to validate
        self.phenopacket = phenopacket

    def validate(self) -> typing.List[ValidationWarning]:
        result = []
        return result


class ProbandValidator(PhenopacketValidator):
    """Helper class that allows to validate ``Phenopacket``s as probands."""

    def __init__(self, proband: Phenopacket):
        super().__init__(proband)
        #: The family to validate
        self.proband = proband

    def validate(self) -> typing.List[ValidationWarning]:
        result = super().validate()
        return result


class RelativeValidator(PhenopacketValidator):
    """Helper class that allows to validate ``Phenopacket``s as relatives."""

    def __init__(self, relative: Phenopacket):
        super().__init__(relative)
        #: The family to validate
        self.relatives = relative

    def validate(self) -> typing.List[ValidationWarning]:
        result = super().validate()
        return result


class PedigreeValidator:
    """Helper class that allows to validate phenopackets pedigree."""

    def __init__(self, sample_names: typing.Set[str], pedigree: Pedigree):
        #: The names of the samples from ``proband`` and ``relatives``.
        self.sample_names = sample_names
        #: The pedigree to validate
        self.pedigree = pedigree

    def validate(self) -> typing.List[ValidationWarning]:
        result = []
        result += self._validate_family_name()
        result += self._validate_sample_names()
        result += self._validate_parent_sexes()
        return result

    def _validate_family_name(self) -> typing.List[ValidationWarning]:
        seen_family_ids = {
            person.family_id for person in self.pedigree.persons if str(person.family_id)
        }
        if len(seen_family_ids) != 1:
            return [ValidationWarning(f"Expected exactly one family, but got {seen_family_ids}.")]
        else:
            return []

    def _validate_sample_names(self) -> typing.List[ValidationWarning]:
        result = []

        ped_names = {person.individual_id for person in self.pedigree.persons}
        if ped_names != self.sample_names:
            result.append(
                ValidationWarning(
                    f"Pedigree sample names {ped_names} do not match proband and "
                    f"relatives {self.sample_names}."
                )
            )

        for person in self.pedigree.persons:
            if person.paternal_id != "0" and person.paternal_id not in ped_names:
                result.append(
                    ValidationWarning(
                        f"Pedigree sample {person.individual_id} has unknown paternal id "
                        f"{person.paternal_id}."
                    )
                )
            if person.maternal_id != "0" and person.maternal_id not in ped_names:
                result.append(
                    ValidationWarning(
                        f"Pedigree sample {person.individual_id} has unknown maternal id "
                        f"{person.maternal_id}."
                    )
                )

        return result

    def _validate_parent_sexes(self) -> typing.List[ValidationWarning]:
        paternal_ids = {
            person.paternal_id for person in self.pedigree.persons if person.paternal_id != "0"
        }
        maternal_ids = {
            person.maternal_id for person in self.pedigree.persons if person.paternal_id != "0"
        }
        result = []
        for person in self.pedigree.persons:
            if person.sex == Sex.MALE and person.individual_id in maternal_ids:
                result.append(
                    ValidationWarning(
                        f"Pedigree sample {person.individual_id} is male but seen as maternal."
                    )
                )
            if person.sex == Sex.FEMALE and person.individual_id in paternal_ids:
                result.append(
                    ValidationWarning(
                        f"Pedigree sample {person.individual_id} is female but seen as paternal."
                    )
                )
        return result


class FileValidator:
    """Helper class that allows to validate phenopackets files."""

    def __init__(self, file_: File):
        #: The file to validate
        self.file = file_

    def validate(self) -> typing.List[ValidationWarning]:
        result = []
        return result


class FamilyValidator:
    """Helper class that allows to validate phenopackets family.

    Note that we currently do not require the ID to be set as we will set it
    automatically when used through the API.
    """

    def __init__(self, family: Family):
        #: The family to validate
        self.family = family
        # The names of the samples from ``proband`` and ``relatives``.  The proband
        # is the first.
        self.sample_names: typing.Set[str] = self._get_sample_names(family)

    def validate(self) -> typing.List[ValidationWarning]:
        """Validate the family and return a potentially empty list of warnings."""
        # Perform the validations per entry.
        result = []
        result += self._validate_meta_data()
        result += self._validate_proband()
        result += self._validate_relatives()
        result += self._validate_pedigree()
        result += self._validate_files()
        return result

    def _get_sample_names(self, family: Family) -> typing.Set[str]:
        """Obtain the sample names from proband and relatives."""
        result = set()
        if str(family.proband):
            result.add(family.proband.id)
        for relative in family.relatives:
            result.add(relative.id)
        return result

    def _validate_meta_data(self) -> typing.List[ValidationWarning]:
        if not str(self.family.meta_data):
            return [MetaDataValidationWarning("Missing /metadata")]
        else:
            return MetaDataValidator(self.family.meta_data).validate()

    def _validate_proband(self) -> typing.List[ValidationWarning]:
        if not str(self.family.proband):
            return [ProbandValidationWarning("Missing /proband")]
        else:
            return ProbandValidator(self.family.proband).validate()

    def _validate_relatives(self) -> typing.List[ValidationWarning]:
        result = []
        for relative in self.family.relatives:
            result += RelativeValidator(relative).validate()
        return result

    def _validate_pedigree(self) -> typing.List[ValidationWarning]:
        if not str(self.family.pedigree):
            return [ValidationWarning("Missing /pedigree")]
        else:
            return PedigreeValidator(self.sample_names, self.family.pedigree).validate()

    def _validate_files(self) -> typing.List[ValidationWarning]:
        result = []
        for file_ in self.family.files:
            result += FileValidator(file_).validate()
        return result
