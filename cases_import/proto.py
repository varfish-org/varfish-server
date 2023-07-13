"""Support for the protocolbuffers in ``cases_import``."""

import typing

from phenopackets import MetaData, Family, Resource, Phenopacket


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


class FamilyValidator:
    """Helper class that allows to validate phenopackets family.

    Note that we currently do not require the ID to be set as we will set it
    automatically when used through the API.
    """

    def __init__(self, family: Family):
        #: The family to validate
        self.family = family

    def validate(self) -> typing.List[ValidationWarning]:
        """Validate the family and return a potentially empty list of warnings."""
        result = []
        # Note that the order of the validation methods is important as they use
        # side effects on collecting information.  This design is not ideal but
        # simplifies the code itself and this is limited to this class.
        result += self._validate_meta_data()
        result += self._validate_proband()
        result += self._validate_relatives()
        result += self._validate_pedigree()
        result += self._validate_files()
        return result

    def _validate_meta_data(self):
        if not self.family.meta_data:
            return [MetaDataValidationWarning("Missing /metadata")]
        else:
            return MetaDataValidator(self.family.meta_data).validate()

    def _validate_proband(self):
        if not self.family.proband:
            return [ProbandValidationWarning("Missing /proband")]
        else:
            return ProbandValidator(self.family.proband).validate()

    def _validate_relatives(self):
        return []

    def _validate_pedigree(self):
        return []

    def _validate_files(self):
        return []
