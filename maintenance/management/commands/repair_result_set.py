from collections import defaultdict
from itertools import chain
import sys
import uuid

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from projectroles.models import Project

from variants.models.case import Case
from variants.models.userannos import AcmgCriteriaRating, SmallVariantComment, SmallVariantFlags


class RollbackException(Exception):
    pass


class Command(BaseCommand):
    """Implementation repairing result sets."""

    #: Help message displayed on the command line.
    help = "Repair query result set for case."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument("--write", help="Perform the actual action.", action="store_true")
        parser.add_argument("--case-uuid", help="UUID of the case to create the query set for.")
        parser.add_argument(
            "--project-uuid", help="UUID of the project to create the query set for all cases."
        )
        parser.add_argument("--all", help="Create query set for all cases.", action="store_true")

    def check_arguments(self, options):
        if bool(options["case_uuid"]) + bool(options["project_uuid"]) + bool(options["all"]) != 1:
            self.stderr.write(self.style.ERROR("Please specify exactly one of the options."))
            sys.exit(1)

        if options["case_uuid"]:
            try:
                Case.objects.get(sodar_uuid=options["case_uuid"])
                msg = "Fixing case {}.".format(options["case_uuid"])
            except Case.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Case with UUID {options['case_uuid']} not found.")
                )
                sys.exit(1)
            except ValidationError as e:
                self.stderr.write(self.style.ERROR(" ".join(e)))
                sys.exit(1)
        elif options["project_uuid"]:
            try:
                Project.objects.get(sodar_uuid=options["project_uuid"])
                msg = "Fixing cases of project {}.".format(options["project_uuid"])
            except Project.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Project with UUID {options['project_uuid']} not found.")
                )
                sys.exit(1)
            except ValidationError as e:
                self.stderr.write(self.style.ERROR(" ".join(e)))
                sys.exit(1)
        elif options["all"]:
            msg = "Creating query set for all cases."
        else:
            self.stderr.write(self.style.ERROR("Please specify exactly one of the options."))
            sys.exit(1)

        self.stdout.write(self.style.NOTICE(msg))

    def handle(self, *args, **options):
        """Generate and fill result sets."""
        self.check_arguments(options)

        try:
            with transaction.atomic():
                if options["case_uuid"]:
                    _case = Case.objects.get(sodar_uuid=options["case_uuid"])
                    self._handle_case(_case)
                elif options["project_uuid"]:
                    for _case in Case.objects.filter(project__sodar_uuid=options["project_uuid"]):
                        self._handle_case(_case)
                elif options["all"]:
                    for _case in Case.objects.all():
                        self._handle_case(_case)

                if not options["write"]:
                    raise RollbackException("Rolling back transaction.")
            self.stderr.write(self.style.SUCCESS("Successfully repaired result set."))

        except RollbackException as e:
            self.stderr.write(self.style.ERROR(e))
            sys.exit(1)

    def _handle_case(self, case):  # noqa: C901
        try:
            case_result_set = case.smallvariantqueryresultset_set.get(smallvariantquery=None)
        except Exception:
            self.stderr.write(self.style.ERROR("No result set for case."))
            sys.exit(1)

        query_result_sets = case.smallvariantqueryresultset_set.filter(
            smallvariantquery__isnull=False
        )
        self.stderr.write(self.style.NOTICE("Deleting old result set."))
        case_result_set.smallvariantqueryresultrow_set.all().delete()
        case_result_set.result_row_count = 0
        case_result_set.save()

        comments = SmallVariantComment.objects.filter(case=case)
        flags = SmallVariantFlags.objects.filter(case=case)
        acmg_ratings = AcmgCriteriaRating.objects.filter(case=case)

        dict_query_result_rows = {}
        for query_result_set in query_result_sets:
            query_result_rows = query_result_set.smallvariantqueryresultrow_set.all()
            for row in query_result_rows:
                key = (
                    f"{row.release}-{row.chromosome}-{row.start}-{row.reference}-{row.alternative}"
                )
                if key not in dict_query_result_rows:
                    dict_query_result_rows[key] = row

        dict_comments = defaultdict(int)
        for comment in comments:
            dict_comments[
                f"{comment.release}-{comment.chromosome}-{comment.start}-{comment.reference}-{comment.alternative}"
            ] += 1

        dict_flags = {
            f"{flag.release}-{flag.chromosome}-{flag.start}-{flag.reference}-{flag.alternative}": flag
            for flag in flags
        }

        dict_acmg_ratings = {
            f"{acmg_rating.release}-{acmg_rating.chromosome}-{acmg_rating.start}-{acmg_rating.reference}-{acmg_rating.alternative}": acmg_rating
            for acmg_rating in acmg_ratings
        }

        dict_query_result_rows_keys = set(dict_query_result_rows.keys())
        dict_comments_keys = set(dict_comments.keys())
        dict_flags_keys = set(dict_flags.keys())
        dict_acmg_ratings_keys = set(dict_acmg_ratings.keys())

        dict_case_result_rows = {}
        for key in dict_query_result_rows_keys:
            if key not in chain(dict_comments_keys, dict_flags_keys, dict_acmg_ratings_keys):
                continue
            self.stderr.write(
                self.style.NOTICE(f"Creating new result row in case result set {key}.")
            )

            row = dict_query_result_rows[key]
            row.pk = None
            row.sodar_uuid = uuid.uuid4()
            row.smallvariantqueryresultset = case_result_set
            row.payload["comment_count"] = 0
            row.payload["flag_count"] = 0
            row.save()

            case_result_set.result_row_count += 1
            case_result_set.save()
            dict_case_result_rows[key] = row

        for key, comment_count in dict_comments.items():
            self.stderr.write(self.style.NOTICE(f"Adding comment to row in case result set {key}."))
            try:
                dict_case_result_rows[key].payload["comment_count"] += comment_count
                dict_case_result_rows[key].save()
            except KeyError:
                self.stderr.write(
                    self.style.ERROR(
                        f"Comment with key {key} not found in case result set {case_result_set.sodar_uuid}."
                    )
                )

        for key, flag in dict_flags.items():
            self.stderr.write(self.style.NOTICE(f"Adding flag to row in case result set {key}."))
            try:
                for field in (
                    "flag_visual",
                    "flag_summary",
                    "flag_candidate",
                    "flag_molecular",
                    "flag_bookmarked",
                    "flag_segregates",
                    "flag_validation",
                    "flag_for_validation",
                    "flag_final_causative",
                    "flag_phenotype_match",
                    "flag_doesnt_segregate",
                    "flag_no_disease_association",
                ):
                    dict_case_result_rows[key].payload[field] = getattr(flag, field)
                dict_case_result_rows[key].payload["flag_count"] += 1
                dict_case_result_rows[key].save()
            except KeyError:
                self.stderr.write(
                    self.style.ERROR(
                        f"Flag with key {key} not found in case result set {case_result_set.sodar_uuid}."
                    )
                )

        for key, acmg_rating in dict_acmg_ratings.items():
            self.stderr.write(
                self.style.NOTICE(f"Adding acmg rating to row in case result set {key}.")
            )
            try:
                dict_case_result_rows[key].payload["acmg_class_auto"] = acmg_rating.class_auto
                dict_case_result_rows[key].payload[
                    "acmg_class_override"
                ] = acmg_rating.class_override
                dict_case_result_rows[key].save()
            except KeyError:
                self.stderr.write(
                    self.style.ERROR(
                        f"Acmg rating with key {key} not found in case result set {case_result_set.sodar_uuid}."
                    )
                )
