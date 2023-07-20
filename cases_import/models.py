import typing
import uuid as uuid_object

from bgjobs.models import (
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    BackgroundJob,
    JobModelMessageMixin,
)
from django.db import models, transaction
from django.urls import reverse
from google.protobuf.json_format import ParseDict, ParseError
import phenopackets
from phenopackets import Family
from projectroles.models import Project

from cases_files.models import (
    AbstractFile,
    IndividualExternalFile,
    IndividualInternalFile,
    PedigreeExternalFile,
    PedigreeInternalFile,
)
from cases_import.proto import get_case_name_from_family_payload
from varfish.utils import JSONField
from variants.models import Case


class CaseImportAction(models.Model):
    """Stores the necessary information for importing a case."""

    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"

    ACTION_CHOICES = (
        (ACTION_CREATE, ACTION_CREATE),
        (ACTION_UPDATE, ACTION_UPDATE),
        (ACTION_DELETE, ACTION_DELETE),
    )

    STATE_DRAFT = "draft"
    STATE_SUBMITTED = "submitted"
    STATE_RUNNING = "running"
    STATE_FAILED = "failed"
    STATE_SUCCESS = "success"

    STATE_CHOICES = (
        (STATE_DRAFT, STATE_DRAFT),
        (STATE_SUBMITTED, STATE_SUBMITTED),
        (STATE_RUNNING, STATE_RUNNING),
        (STATE_FAILED, STATE_FAILED),
        (STATE_SUCCESS, STATE_SUCCESS),
    )

    #: Record UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True)

    #: The project that the import is related to.
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    #: The action to perform.
    action = models.CharField(
        max_length=32, null=False, blank=False, choices=ACTION_CHOICES, default=ACTION_CREATE
    )
    #: The import action's current state.
    state = models.CharField(
        max_length=32, null=False, blank=False, choices=STATE_CHOICES, default=STATE_DRAFT
    )
    #: The JSON serialization of the phenopacket that is to be used in the action.
    payload = JSONField()

    #: Whether or not to overwrite changes in the disease and phenotype terms.
    #:
    #: These are commonly curated by users so we do not want to override them with potentially
    #: empty or wrong lists.
    overwrite_terms = models.BooleanField(default=False)

    def get_case_name(self):
        """Return case name from ``self.payload`` as family ID."""
        return get_case_name_from_family_payload(self.payload)

    class Meta:
        #: Order by date of last modification (most recent first).
        ordering = ("-date_modified",)


class CaseImportBackgroundJobManager(models.Manager):
    """Custom manager class that allows to create a ``CaseImportBackgroundJob``
    together with the backing ``BackgroundJob``.
    """

    def create_full(self, *, caseimportaction, project, user):
        case_name = caseimportaction.get_case_name()
        bg_job = BackgroundJob.objects.create(
            name=f"Import of case '{case_name}'",
            project=project,
            job_type=CaseImportBackgroundJob.spec_name,
            user=user,
        )
        instance = super().create(project=project, bg_job=bg_job, caseimportaction=caseimportaction)
        return instance


class CaseImportBackgroundJob(JobModelMessageMixin, models.Model):
    """Background job for importing cases with the ``cases_import`` app."""

    # We use a custom manager that provides creation together with the ``BackgroundJob``.
    objects = CaseImportBackgroundJobManager()

    #: Task description for logging.
    task_desc = "Case Import"

    #: String identifying model in BackgroundJob.
    spec_name = "cases_import.importcasebgjob"

    #: The SODAR UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4,
        unique=True,
    )
    #: The project that this background job belong to.
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )

    #: The background job for state management etc.
    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="caseimportbackgroundjob",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )
    #: The case import action to perform.
    caseimportaction = models.ForeignKey(CaseImportAction, on_delete=models.CASCADE, null=False)

    def get_human_readable_type(self):
        return "Import a case into VarFish"

    def get_absolute_url(self):
        return reverse(
            "cases_import:ui-caseimportbackgroundjob-detail",
            kwargs={"caseimportbackgroundjob": self.sodar_uuid},
        )


def build_legacy_pedigree(family: Family) -> typing.List:
    """Build a legacy pedigree from the ``phenopackets.Family``.

    This code will go away once we got rid of the legacy ``pedigree`` member.  We are using
    direct dict access below so we are not robust in phenopackets protobuf updates but that
    should be fair as we will get rid of the legacy ``pedigree`` anyway.
    """
    has_measurements = {
        family.proband.id: bool(len(family.proband.measurements)),
    }
    for relative in family.relatives:
        has_measurements[relative.id] = bool(len(relative.measurements))

    sex_map = {
        phenopackets.Sex.MALE: 1,
        phenopackets.Sex.FEMALE: 2,
        phenopackets.Sex.OTHER_SEX: 0,
        phenopackets.Sex.UNKNOWN_SEX: 0,
    }

    affected_map = {
        2: 2,
        1: 1,
        0: 0,
    }

    result = []
    for person in family.pedigree.persons:
        result.append(
            {
                "sex": sex_map[person.sex],
                "patient": person.individual_id,
                "father": person.paternal_id,
                "mother": person.maternal_id,
                "affected": affected_map[person.affected_status],
                "has_gt_entries": has_measurements[person.individual_id],
            }
        )
    return result


def release_from_family(family: Family) -> typing.Optional[str]:
    """Obtain the genome release from the given family (index)'s target file.

    Return ``None`` if the release cannot be determined.
    """
    if (
        family
        and family.proband
        and len(family.proband.files)
        and "genomebuild" in family.proband.files[0].file_attributes
    ):
        val = family.proband.files[0].file_attributes["genomebuild"]
        if val == "GRCh37":
            return AbstractFile.GENOMEBUILD_GRCH37
        elif val == "GRCh38":
            return AbstractFile.GENOMEBUILD_GRCH38
    return None


class CaseImportBackgroundJobExecutor:
    """Implementation of ``CaseImportBackgroundJob`` execution."""

    def __init__(self, job_pk: int):
        #: Job record primary key.
        self.job_pk = job_pk
        #: The ``CaseImportBackgroundJob`` object itself.
        self.caseimportbackgroundjob = CaseImportBackgroundJob.objects.get(pk=self.job_pk)

    def run(self):
        """Execute the case import."""
        with self.caseimportbackgroundjob.marks():
            self._run()

    def _run(self):
        if self.caseimportbackgroundjob.action == CaseImportAction.ACTION_DELETE:
            self._run_delete()
        else:
            self._run_create_or_update()

    def _get_case(self) -> typing.Optional[Case]:
        """Return the case belonging to the job."""
        project = self.caseimportbackgroundjob.project
        case_name = self.caseimportbackgroundjob.caseimportaction.get_case_name()
        return Case.objects.first(project=project, name=case_name)

    def _run_delete(self) -> Case:
        case = self._get_case()
        if case:
            case.delete()
            self.caseimportbackgroundjob.add_log_entry("Case has been deleted successfully")
        else:
            self.caseimportbackgroundjob.add_log_entry(
                "Case to delete not found, skipping", LOG_LEVEL_WARNING
            )

    def _run_create_or_update(self):
        # Creation of the new, empty case or updating the case state of an existing one is
        # done in a transaction as that's quick and we cannot use in-flight issues.
        with transaction.atomic():
            # Create a new case or update the existing on'es state to "updating".
            case = self._create_or_update_case()
        if not case:
            return  # break out, logging happend in ``self._create_or_update_case()``.
        if self.caseimportbackgroundjob.caseimportaction.action == CaseImportAction.ACTION_UPDATE:
            # Clear the external and internal files, will be re-created during import.
            self._clear_files(case)
        # Create the external files entries.
        self._create_external_files(case)
        # Actually perform the seqvars annotation with mehari.
        self._run_seqvars_annotation(case)
        # Actually perform the strucvars annotation with mehari.
        self._run_strucvars_annotation(case)
        # Update the case state to "done".
        self._update_case_state(case)

    def _create_or_update_case(self) -> typing.Optional[Case]:
        caseimportaction = self.caseimportbackgroundjob.caseimportaction
        try:
            family: Family = ParseDict(js_dict=caseimportaction.payload, message=Family())
        except ParseError as e:
            self.caseimportbackgroundjob.add_log_entry(
                f"Problem loading phenopackets.Family: {e}", LOG_LEVEL_ERROR
            )
            raise

        if caseimportaction.action == CaseImportAction.ACTION_CREATE:
            self.caseimportbackgroundjob.add_log_entry("Creating new case")
            return self._create_case(family)
        else:
            self.caseimportbackgroundjob.add_log_entry("Updating existing case")
            return self._update_case(family)

    def _create_case(self, family: Family) -> Case:
        caseimportaction = self.caseimportbackgroundjob.caseimportaction
        return Case.objects.create(
            case_version=2,
            state=Case.STATE_IMPORTING,
            project=self.caseimportbackgroundjob.project,
            release=release_from_family(family),
            name=caseimportaction.get_case_name(),
            index=family.proband.id,
            pedigree=build_legacy_pedigree(family),
        )

    def _update_case(self, family: Family) -> typing.Optional[Case]:
        caseimportaction = self.caseimportbackgroundjob.caseimportaction
        case = self._get_case()
        if not case:
            self.caseimportbackgroundjob.add_log_entry(
                "Could not find case to update", LOG_LEVEL_ERROR
            )
            return None

        case.case_version = 2
        case.state = Case.STATE_UPDATING
        case.release = release_from_family(family)
        case.name = caseimportaction.get_case_name()
        case.index = family.proband.id
        case.pedigree = build_legacy_pedigree(family)
        case.save()

        return case

    def _clear_files(self, case: Case):
        pedigree = case.pedigree_obj
        internal_files = list(PedigreeInternalFile.objects.filter(pedigree=pedigree))
        external_files = list(PedigreeExternalFile.objects.filter(pedigree=pedigree))
        for individual in pedigree.individual_set.all():
            internal_files += list(IndividualInternalFile.objects.filter(individual=individual))
            external_files += list(IndividualExternalFile.objects.filter(individual=individual))
        self.caseimportbackgroundjob.add_log_entry(
            "Deleting {} internal and {} external file references".format(
                len(internal_files), len(external_files)
            ),
            LOG_LEVEL_INFO,
        )
        for obj in internal_files + external_files:
            obj.delete()

    def _create_external_files(self, case: Case):
        assert False, "Implement me!"  # 1

    def _run_seqvars_annotation(self, case: Case):
        self.caseimportbackgroundjob.add_log_entry("seqvars annotation not implemented yet")

    def _run_strucvars_annotation(self, case: Case):
        self.caseimportbackgroundjob.add_log_entry("strucvars annotation not implemented yet")

    def _update_case_state(self, case):
        case.state = Case.STATE_DONE
        case.save()


def run_caseimportactionbackgroundjob(*, pk: int):
    """Execute the work for a ``CaseImportBackgroundJob``."""
    executor = CaseImportBackgroundJobExecutor(pk)
    executor.run()
