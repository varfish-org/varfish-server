"""Django command for importing a case after annotation with ``varfish-annotator``."""

import gzip
import itertools
import json
import tempfile

import aldjemy
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from sqlalchemy import delete

from svs.models import StructuralVariant, StructuralVariantGeneAnnotation, StructuralVariantSet
from projectroles.models import Project
from projectroles.plugins import get_backend_api
from variants.models import SmallVariant, Case, AnnotationReleaseInfo, SmallVariantSet
from variants.variant_stats import rebuild_case_variant_stats
from variants.tasks import update_variant_counts
from ..helpers import tsv_reader


#: The User model to use.
User = get_user_model()


#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


def open_file(path, mode):
    """Open gzip or normal file."""
    if path.endswith(".gz"):
        return gzip.open(path, mode)
    else:
        return open(path, mode)


class Command(BaseCommand):
    """Implementation of importing a case from pedigree, variants, and genotype file.

    The necessary steps are:

    - Create a new ``Case`` in the appropriate ``Project`` (specified by UUID)
    - Import the variant ``Annotation`` records for the case's variants
    - Import the ``SmallVariant`` call information

    All steps are executed in a transaction, so no stale state is left in the database.
    """

    #: Help message displayed on the command line.
    help = "Import case from PED file and varfish-annotator output."

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

    def handle(self, *args, **options):
        """The actual implementation is in ``_handle()``, splitting to get commit times."""
        # Flatten the nargs="+" arguments.
        options["path_genotypes"] = list(itertools.chain(*options["path_genotypes"]))
        options["path_db_info"] = list(itertools.chain(*options["path_db_info"]))
        if options["path_feature_effects"]:
            options["path_feature_effects"] = list(
                itertools.chain(*options["path_feature_effects"])
            )
        # Perform the actual import.
        self._handle(*args, **options)
        if self.last_now:
            elapsed = timezone.now() - self.last_now
            self.stdout.write("Database commit took %.2f s" % elapsed.total_seconds())

    def _handle(self, *args, **options):
        """Perform the import of the case."""
        self.stdout.write("Starting case import")
        self.stdout.write("options = %s" % options)
        self.last_now = None

        # Fetch ``User`` object to use for the importer/owner
        try:
            self.stdout.write("Importing as admin: {}".format(settings.PROJECTROLES_ADMIN_OWNER))
            admin = User.objects.get(username=settings.PROJECTROLES_ADMIN_OWNER)
        except User.DoesNotExist as e:
            raise CommandError(
                "Could not get configured admin user for import with username {}".format(
                    settings.PROJECTROLES_ADMIN_OWNER
                )
            ) from e

        # TODO: properly implement transactional behaviour for small variants where we are not in a transaction...

        # Get project, create case with pedigree.
        project = self._get_project(options["project_uuid"])
        existing_cases = Case.objects.filter(name=options["case_name"], project=project)

        if existing_cases.exists():
            if not options["force"]:
                raise CommandError("Case already imported. To update case, use the --force flag.")
            prev_case = existing_cases.first()
        else:
            prev_case = None

        samples_in_genotypes = self._get_samples_in_genotypes(options["path_genotypes"][0])
        case = self._create_or_update_case(
            project,
            options["case_name"],
            options["index_name"],
            options["path_ped"],
            samples_in_genotypes,
            options["path_db_info"],
            prev_case,
            options["path_feature_effects"] is None,
        )

        # Import small or structural variants
        if not options["path_feature_effects"]:
            smallvariant_table = aldjemy.core.get_meta().tables["variants_smallvariant"]
            variant_set = case.smallvariantset_set.create(state="importing")
            try:
                self._import_small_variants_genotypes(variant_set, options["path_genotypes"][0])
                self._rebuild_small_variants_stats(variant_set)
                SmallVariantSet.objects.filter(pk=variant_set.id).update(state="active")
            except Exception as e:
                # TODO: need background job to help with deleting old data...
                self.stdout.write(
                    self.style.ERROR("Import was not successful. (%s) Rolling back." % e)
                )
                SmallVariantSet.objects.filter(pk=variant_set.id).update(state="deleting")
                SQLALCHEMY_ENGINE.execute(
                    smallvariant_table.delete().where(smallvariant_table.c.set_id == variant_set.id)
                )
                SmallVariantSet.objects.get(pk=variant_set.id).delete()
                raise e  # re-raise
            else:
                self.stdout.write("Removing old variant set")
                keep = None
                delete_ids = []
                with transaction.atomic():
                    for var_set in SmallVariantSet.objects.order_by("-date_created"):
                        if var_set.state == "active" and keep is None:
                            keep = var_set
                        else:
                            delete_ids.append(var_set.pk)
                            var_set.state = "deleting"
                            var_set.save()
                SQLALCHEMY_ENGINE.execute(
                    smallvariant_table.delete().where(smallvariant_table.c.set_id.in_(delete_ids))
                )
                with transaction.atomic():
                    for var_set in SmallVariantSet.objects.filter(id__in=delete_ids):
                        var_set.delete()
            # Update small and structural variant counts.
            update_variant_counts(case, variant_set)
        else:
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
                    "Number of files specified by --path-genotypes, --path-feature-effects, "
                    "and --path-db-info must be the same"
                )
            sv_table = aldjemy.core.get_meta().tables["variants_structuralvariant"]
            geneanno_table = aldjemy.core.get_meta().tables[
                "variants_structuralvariantgeneannotation"
            ]
            variant_set = case.structuralvariantset_set.create(state="importing")
            try:
                self._import_structural_variants_genotypes(variant_set, options["path_genotypes"])
                self._import_structural_variants_feature_effects(
                    variant_set, options["path_feature_effects"]
                )
            except Exception as e:
                # TODO: need background job to help with deleting old data...
                self.stdout.write(
                    self.style.ERROR("Import was not successful. (%s) Rolling back." % e)
                )
                SmallVariantSet.objects.filter(pk=variant_set.id).update(state="deleting")
                SQLALCHEMY_ENGINE.execute(
                    sv_table.delete().where(sv_table.c.set_id == variant_set.id)
                )
                SQLALCHEMY_ENGINE.execute(
                    geneanno_table.delete().where(geneanno_table.c.set_id == variant_set.id)
                )
                SmallVariantSet.objects.get(pk=variant_set.id).delete()
                raise e  # re-raise
            else:
                self.stdout.write("Removing old variant set")
                keep = None
                delete_ids = []
                with transaction.atomic():
                    for var_set in StructuralVariantSet.objects.order_by("-date_created"):
                        if var_set.state == "active" and keep is None:
                            keep = var_set
                        else:
                            delete_ids.append(var_set.pk)
                            var_set.state = "deleting"
                            var_set.save()
                SQLALCHEMY_ENGINE.execute(
                    sv_table.delete().where(sv_table.c.set_id.in_(delete_ids))
                )
                SQLALCHEMY_ENGINE.execute(
                    geneanno_table.delete().where(sv_table.c.set_id.in_(delete_ids))
                )
                with transaction.atomic():
                    for var_set in StructuralVariantSet.objects.filter(id__in=delete_ids):
                        var_set.delete()
            # Update small and structural variant counts.
            update_variant_counts(case)

        # Register import action in the timeline
        timeline = get_backend_api("timeline_backend")
        if timeline:
            timeline.add_event(
                project=project,
                app_name="variants",
                user=admin,
                event_name="case_import",
                description='Import of case "{}" finished.'.format(case.name),
                status_type="OK",
            )
        self.last_now = timezone.now()

    def _get_project(self, project_uuid):
        """Get query or raise appropriate exception."""
        try:
            return Project.objects.get(sodar_uuid=project_uuid)
        except ObjectDoesNotExist:
            raise CommandError("Project with UUID {} does not exist".format(project_uuid))

    def _get_samples_in_genotypes(self, path_genotypes):
        """Return names from samples present in genotypes column."""
        with open_file(path_genotypes, "rt") as tsv:
            header = tsv.readline()[:-1].split("\t")
            first = tsv.readline()[:-1].replace('"""', '"').split("\t")
            values = dict(zip(header, first))
            return list(json.loads(values["genotype"]).keys())

    def _create_or_update_case(
        self,
        project,
        case_name,
        index_name,
        path_ped,
        samples_in_genotypes,
        path_db_info,
        prev_case=None,
        is_small_var=True,
    ):
        """Create ``Case`` object, update if it exists and remove old data associated with it."""
        self.stdout.write("Reading PED and creating case...")
        # Build pedigree
        pedigree = []
        seen_index = False
        with open(path_ped, "rt") as pedf:
            for line in pedf:
                line = line.strip()
                _, patient, father, mother, sex, affected = line.split("\t")
                seen_index = seen_index or patient == index_name
                sex = int(sex)
                affected = int(affected)
                pedigree.append(
                    {
                        "patient": patient,
                        "father": father,
                        "mother": mother,
                        "sex": sex,
                        "affected": affected,
                        "has_gt_entries": patient in samples_in_genotypes,
                    }
                )
        if not seen_index:
            raise CommandError("Index {} not seen in pedigree!".format(index_name))
        # Construct or retrieve ``Case`` object
        if prev_case:
            case = prev_case
            case.index = index_name
            case.pedigree = pedigree
            case.save()
            # Remove old data associated with case
            if is_small_var:
                self.stdout.write("Removing old small variant data associated with the case...")
                before = timezone.now()
                AnnotationReleaseInfo.objects.filter(case=case).delete()
                res_s = aldjemy.core.get_meta().tables["variants_smallvariantquery_query_results"]
                res_c = aldjemy.core.get_meta().tables["variants_clinvarquery_query_results"]
                res_p = aldjemy.core.get_meta().tables[
                    "variants_projectcasessmallvariantquery_query_results"
                ]
                SQLALCHEMY_ENGINE.execute(
                    res_s.delete()
                    .where(res_s.c.smallvariant_id == SmallVariant.sa.id)
                    .where(SmallVariant.sa.case_id == case.pk)
                )
                SQLALCHEMY_ENGINE.execute(
                    res_c.delete()
                    .where(res_c.c.smallvariant_id == SmallVariant.sa.id)
                    .where(SmallVariant.sa.case_id == case.pk)
                )
                SQLALCHEMY_ENGINE.execute(
                    res_p.delete()
                    .where(res_p.c.smallvariant_id == SmallVariant.sa.id)
                    .where(SmallVariant.sa.case_id == case.pk)
                )
                SQLALCHEMY_ENGINE.execute(
                    SmallVariant.sa.table.delete().where(SmallVariant.sa.case_id == case.pk)
                )
            else:
                self.stdout.write(
                    "Removing old structural variant data associated with the case..."
                )
                before = timezone.now()
                stmt = (
                    delete(StructuralVariantGeneAnnotation.sa)
                    .where(
                        StructuralVariantGeneAnnotation.sa.sv_uuid == StructuralVariant.sa.sv_uuid
                    )
                    .where(StructuralVariant.sa.case_id == case.pk)
                )
                SQLALCHEMY_ENGINE.execute(stmt)
                StructuralVariant.objects.filter(case_id=case.pk).delete()
            elapsed = timezone.now() - before
            self.stdout.write(
                self.style.SUCCESS(
                    "Done removing old data associated with the case in %.2f s"
                    % elapsed.total_seconds()
                )
            )
        else:
            case = Case.objects.create(
                name=case_name, project=project, index=index_name, pedigree=pedigree
            )
        # Import the release info.
        for entry in tsv_reader(path_db_info[0]):
            AnnotationReleaseInfo.objects.get_or_create(
                genomebuild=entry["genomebuild"],
                table=entry["db_name"],
                case=case,
                defaults={"release": entry["release"]},
            )

        if prev_case:
            self.stdout.write(self.style.SUCCESS("Retrieved existing case."))
        else:
            self.stdout.write(self.style.SUCCESS("Done creating case."))
        return case

    def _import_small_variants_genotypes(self, variant_set, path_genotypes):
        """Import small variants TSV file into database."""
        before = timezone.now()
        self.stdout.write("Creating temporary genotype file...")
        with tempfile.NamedTemporaryFile("w+t") as tempf:
            with open_file(path_genotypes, "rt") as inputf:
                header = inputf.readline().strip()
                try:
                    case_idx = header.split("\t").index("case_id")
                    set_idx = header.split("\t").index("set_id")
                except ValueError as e:
                    raise CommandError(
                        "Column 'case_id' or 'set_id' not found in genotypes TSV"
                    ) from e
                tempf.write(header)
                tempf.write("\n")
                while True:
                    line = inputf.readline().strip()
                    if not line:
                        break
                    arr = line.split("\t")
                    arr[case_idx] = str(variant_set.case.pk)
                    arr[set_idx] = str(variant_set.pk)
                    tempf.write("\t".join(arr))
                    tempf.write("\n")
            tempf.flush()
            elapsed = timezone.now() - before
            self.stdout.write("Wrote file in %.2f s" % elapsed.total_seconds())
            before = timezone.now()
            self.stdout.write("Importing genotype file...")
            SmallVariant.objects.from_csv(
                tempf.name,
                delimiter="\t",
                null=".",
                ignore_conflicts=True,
                drop_constraints=False,
                drop_indexes=False,
            )
            elapsed = timezone.now() - before
            self.stdout.write(
                self.style.SUCCESS(
                    "Finished importing genotypes in %.2f s" % elapsed.total_seconds()
                )
            )

    def _rebuild_small_variants_stats(self, variant_set):
        """Rebuild small variant statistics."""
        before = timezone.now()
        self.stdout.write("Computing variant statistics...")
        rebuild_case_variant_stats(SQLALCHEMY_ENGINE, variant_set)
        elapsed = timezone.now() - before
        self.stdout.write(
            self.style.SUCCESS(
                "Finished computing variant statistics in %.2f s" % elapsed.total_seconds()
            )
        )

    def _import_structural_variants_genotypes(self, variant_set, path_genotypes):
        """Import structural variants TSV file into database."""
        self.stdout.write("Creating temporary SV genotype file...")
        with tempfile.NamedTemporaryFile("w+t") as tempf:
            for file_no, current_path in enumerate(path_genotypes):
                with open_file(current_path, "rt") as inputf:
                    header = inputf.readline().strip()
                    try:
                        case_idx = header.split("\t").index("case_id")
                        set_idx = header.split("\t").index("set_id")
                    except ValueError as e:
                        raise CommandError(
                            "Column 'case_id' or 'set_id' not found in genotypes TSV"
                        ) from e
                    if file_no == 0:
                        tempf.write(header)
                        tempf.write("\n")
                    while True:
                        line = inputf.readline().strip()
                        if not line:
                            break
                        arr = line.split("\t")
                        arr[case_idx] = str(variant_set.case.pk)
                        arr[set_idx] = str(variant_set.pk)
                        tempf.write("\t".join(arr))
                        tempf.write("\n")
            tempf.flush()
            self.stdout.write("Importing SV genotype file...")
            StructuralVariant.objects.from_csv(
                tempf.name,
                delimiter="\t",
                null=".",
                ignore_conflicts=True,
                drop_constraints=False,
                drop_indexes=False,
            )
            self.stdout.write(self.style.SUCCESS("Finished importing SV genotypes"))

    def _import_structural_variants_feature_effects(self, variant_set, path_feature_effects):
        """Import structural variants TSV file into database."""
        self.stdout.write("Creating temporary SV feature effects file...")
        with tempfile.NamedTemporaryFile("w+t") as tempf:
            for file_no, current_path in enumerate(path_feature_effects):
                with open_file(current_path, "rt") as inputf:
                    header = inputf.readline().strip()
                    try:
                        case_idx = header.split("\t").index("case_id")
                        set_idx = header.split("\t").index("set_id")
                    except ValueError as e:
                        raise CommandError(
                            "Column 'case_id' or 'set_id' not found in SV feature effects TSV"
                        ) from e
                    if file_no == 0:
                        tempf.write(header)
                        tempf.write("\n")
                    while True:
                        line = inputf.readline().strip()
                        if not line:
                            break
                        arr = line.split("\t")
                        arr[case_idx] = str(variant_set.case.pk)
                        arr[set_idx] = str(variant_set.pk)
                        tempf.write("\t".join(arr))
                        tempf.write("\n")
            tempf.flush()
            self.stdout.write("Importing SV feature effects...")
            StructuralVariantGeneAnnotation.objects.from_csv(
                tempf.name,
                delimiter="\t",
                null=".",
                ignore_conflicts=True,
                drop_constraints=False,
                drop_indexes=False,
            )
            self.stdout.write(self.style.SUCCESS("Finished importing SV feature effects"))
