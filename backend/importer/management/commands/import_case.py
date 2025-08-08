"""Django command for importing a case after annotation with ``varfish-annotator``."""

import gzip
import itertools
import os.path

from bgjobs.models import BackgroundJob
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from projectroles.models import Project

from svs.models import ImportStructuralVariantBgJob
from svs.tasks import run_import_structural_variants_bg_job
from variants.models import ImportVariantsBgJob
from variants.tasks import run_import_variants_bg_job

#: The User model to use.
User = get_user_model()


def open_file(path, mode):
    """Open gzip or normal file."""
    if path.endswith(".gz"):
        return gzip.open(path, mode)
    else:
        return open(path, mode)


class CaseImportBase:
    def _import_small_variants(self, options, project, user):
        if len(options["path_genotypes"]) != len(options["path_db_info"]):
            raise CommandError(
                "Number of --path-genotypes, and--path-db-info arguments has to be the same"
            )
        with transaction.atomic():
            # The background job creation must be atomic.
            bg_job = BackgroundJob.objects.create(
                name="Import of case %s" % options["case_name"],
                project=project,
                job_type=ImportVariantsBgJob.spec_name,
                user=user,
            )
            import_job = ImportVariantsBgJob.objects.create(
                bg_job=bg_job,
                project=project,
                case_name=options["case_name"],
                index_name=options["index_name"],
                path_ped=options["path_ped"],
                path_genotypes=options["path_genotypes"],
                path_db_info=options["path_db_info"],
                path_bam_qc=options["path_bam_qc"],
            )
        if options["sync"]:
            self.stdout.write("Running import job now synchronously")
            run_import_variants_bg_job(import_job.pk)
            self.stdout.write(self.style.SUCCESS("Done importing."))
        else:
            self.stdout.write("Running import job as background job")
            run_import_variants_bg_job.delay(import_job.pk)
            self.stdout.write(
                self.style.SUCCESS("Created variants import job %s" % import_job.get_absolute_url())
            )

    def _import_structural_variants(self, options, project, user):
        if (
            len(
                {
                    len(options["path_genotypes"]),
                    len(options["path_feature_effects"]),
                    len(options["path_db_info"]),
                }
            )
            != 1
        ):
            raise CommandError(
                "Number of --path-genotypes, --path-feature-effects, and "
                "--path-db-info arguments has to be the same"
            )

        with transaction.atomic():
            # The background job creation must be atomic.
            bg_job = BackgroundJob.objects.create(
                name="Import of case %s" % options["case_name"],
                project=project,
                job_type=ImportStructuralVariantBgJob.spec_name,
                user=user,
            )
            import_job = ImportStructuralVariantBgJob.objects.create(
                bg_job=bg_job,
                project=project,
                case_name=options["case_name"],
                index_name=options["index_name"],
                path_ped=options["path_ped"],
                path_genotypes=options["path_genotypes"],
                path_feature_effects=options["path_feature_effects"],
                path_db_info=options["path_db_info"],
            )
        if options["sync"]:
            self.stdout.write("Running import job now synchronously")
            run_import_structural_variants_bg_job(import_job.pk)
            self.stdout.write(self.style.SUCCESS("Done importing."))
        else:
            self.stdout.write("Running import job as background job")
            run_import_structural_variants_bg_job.delay(import_job.pk)
            self.stdout.write(
                self.style.SUCCESS("Created SV import job %s" % import_job.get_absolute_url())
            )

    def _run(self, *args, **options):
        self.stdout.write("Starting import with options = %s" % options)

        for path in itertools.chain(
            [options["path_ped"]],
            options["path_genotypes"],
            options["path_feature_effects"],
            options["path_db_info"],
        ):
            if not os.path.exists(path):
                raise CommandError("File does not exist: %s" % path)

        try:
            self.stdout.write(
                "Creating import task as {}".format(settings.PROJECTROLES_ADMIN_OWNER)
            )
            user = User.objects.get(username=settings.PROJECTROLES_ADMIN_OWNER)
        except User.DoesNotExist as e:
            raise CommandError(
                "Could not get configured admin user for import with username {}".format(
                    settings.PROJECTROLES_ADMIN_OWNER
                )
            ) from e
        project = Project.objects.get(sodar_uuid=options["project_uuid"])

        # Perform the actual import.
        if not options["path_feature_effects"]:
            return self._import_small_variants(options, project, user)
        else:
            return self._import_structural_variants(options, project, user)


class Command(CaseImportBase, BaseCommand):
    """Implementation of importing a case from pedigree, variants, and genotype file.

    The necessary steps are:

    - Create a new ``Case`` in the appropriate ``Project`` (specified by UUID)
    - Import the variant ``Annotation`` records for the case's variants
    - Import the ``SmallVariant`` call information

    All steps are executed in a transaction, so no stale state is left in the database.
    """

    #: Help message displayed on the command line.
    help = "Import case from PED file and varfish-annotator output. DEPRECATED"

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument("--case-name", help="Name to assign to the case", required=True)
        parser.add_argument("--index-name", help="The name of the index sample", required=True)
        parser.add_argument("--path-ped", help="Path to pedigree input file", required=True)
        parser.add_argument(
            "--path-genotypes",
            help="Path to genotypes TSV file",
            required=True,
            action="append",
            default=[],
            nargs="+",
        )
        parser.add_argument(
            "--path-bam-qc",
            help="Path to BAM QC file.",
            required=False,
            action="append",
            default=[],
            nargs="+",
        )
        parser.add_argument(
            "--path-feature-effects",
            help="Path to gene-wise feature effects (triggers import of structural variants)",
            action="append",
            default=[],
            nargs="+",
        )
        parser.add_argument(
            "--path-db-info",
            help="Path to database import info TSV file",
            required=True,
            action="append",
            default=[],
            nargs="+",
        )
        parser.add_argument(
            "--project-uuid", help="UUID of the project to add the case to", required=True
        )
        parser.add_argument(
            "--force", help="Replace imported case if it exists", action="store_true"
        )
        parser.add_argument(
            "--sync", action="store_true", default=False, help="Don't run as background job"
        )

    def handle(self, *args, **options):
        """The actual implementation is in ``_handle()``, splitting to get commit times."""
        # Flatten the nargs="+" arguments.
        self.stdout.write(self.style.NOTICE("!!! THIS COMMAND IS MARKED AS DEPCREATED !!!"))
        self.stdout.write(self.style.NOTICE("Please use the varfish-cli instead."))
        options["path_genotypes"] = list(itertools.chain(*options["path_genotypes"]))
        options["path_bam_qc"] = list(itertools.chain(*options["path_bam_qc"]))
        options["path_db_info"] = list(itertools.chain(*options["path_db_info"]))
        if options["path_feature_effects"]:
            options["path_feature_effects"] = list(
                itertools.chain(*options["path_feature_effects"])
            )

        self._run(*args, **options)
