"""Django command for generating query result sets."""

import json
import sys

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from projectroles.models import Project

from variants.models import Case
from variants.tasks import create_queryresultset as task_create_queryresultset
from variants.utils import create_queryresultset

MSG_RESULT_SETS_CREATED = """
- SmallVariantQueryResultSets created: {smallvariantqueryresultset}
- SvQueryResultSets created: {svqueryresultset}
- SmallVariantQueryResultSets:
  - Added: {sms_added}
  - Removed: {sms_removed}
- SvQueryResultSets:
  - Added: {svs_added}
  - Removed: {svs_removed}"""

MSG_RESULT_SETS_NOTHING = """
- Nothing to do."""

MSG_RESULT_SETS_WARNING = """
WARNING! There are orphaned annotations:
- SmallVariant annotations:
  - Salvable:
    - Flags: {sms_salvable_flags}
    - Comments: {sms_salvable_comments}
    - ACMG ratings: {sms_salvable_acmg_ratings}
  - Lost:
    - Flags: {sms_lost_flags}
    - Comments: {sms_lost_comments}
    - ACMG ratings: {sms_lost_acmg_ratings}
- StructuralVariant annotations:
  - Salvable:
    - Flags: {svs_salvable_flags}
    - Comments: {svs_salvable_comments}
  - Lost:
    - Flags: {svs_lost_flags}
    - Comments: {svs_lost_comments}""".lstrip()

MSG_DUPLICATES_WARNING = """
WARNING! There are duplicate variants:
- Duplicate small variants: {duplicates_sms}
- Duplicate structural variants: {duplicates_svs}""".lstrip()

TSV_HEADER_DUPLICATES = "case_uuid\tproject\tcase_name\tregion\tjson\n"
TSV_LINE_DUPLICATES = "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{json}\n"

TSV_HEADER_FLAGS = "case_uuid\tproject\tcase_name\tregion\tlost\tflag_molecular\tflag_visual\tflag_validation\tflag_phenotype_match\tflag_summary\tjson\n"
TSV_LINE_FLAGS = "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{lost}\t{flag_molecular}\t{flag_visual}\t{flag_validation}\t{flag_phenotype_match}\t{flag_summary}\t{json}\n"

TSV_HEADER_COMMENTS = "case_uuid\tproject\tcase_name\tregion\tlost\tcomment\tjson\n"
TSV_LINE_COMMENTS = (
    "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{lost}\t{comment}\t{json}\n"
)

TSV_HEADER_SIMPLE = "case_uuid\tproject\tcase_name\tregion\tlost\tjson\n"
TSV_LINE_SIMPLE = (
    "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{lost}\t{json}\n"
)


def write_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=1)


def write_tsv_simple(filename, header, line_fmt, data):
    with open(filename, "w") as f:
        f.write(header)
        for line in data:
            f.write(line_fmt.format(**line))


def write_tsv_flags(filename, header, line_fmt, data):
    with open(filename, "w") as f:
        f.write(header)
        for line in data:
            j = json.loads(line["json"])
            f.write(
                line_fmt.format(
                    **line,
                    flag_molecular=j["flag_molecular"],
                    flag_visual=j["flag_visual"],
                    flag_validation=j["flag_validation"],
                    flag_phenotype_match=j["flag_phenotype_match"],
                    flag_summary=j["flag_summary"],
                )
            )


def write_tsv_comments(filename, header, line_fmt, data):
    with open(filename, "w") as f:
        f.write(header)
        for line in data:
            j = json.loads(line["json"])
            f.write(
                line_fmt.format(
                    **line,
                    comment=j["text"],
                )
            )


class Command(BaseCommand):
    """Implementation of clearing expired exported files."""

    #: Help message displayed on the command line.
    help = "Generate query result set for case."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--async", help="Run the creating asynchronously.", action="store_false"
        )
        parser.add_argument("--case-uuid", help="UUID of the case to create the query set for.")
        parser.add_argument(
            "--project-uuid", help="UUID of the project to create the query set for all cases."
        )
        parser.add_argument("--all", help="Create query set for all cases.", action="store_true")

    def check_arguments(self, options):
        if bool(options["case_uuid"]) + bool(options["project_uuid"]) + bool(options["all"]) != 1:
            self.stderr.write(self.style.ERROR("Please specify exactly one of the options."))
            sys.exit(0)

        if options["case_uuid"]:
            try:
                Case.objects.get(sodar_uuid=options["case_uuid"])
                msg = "Creating query set for case {}.".format(options["case_uuid"])
            except Case.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Case with UUID {options['case_uuid']} not found.")
                )
                sys.exit(0)
            except ValidationError as e:
                self.stderr.write(self.style.ERROR(" ".join(e)))
                sys.exit(0)
        elif options["project_uuid"]:
            try:
                Project.objects.get(sodar_uuid=options["project_uuid"])
                msg = "Creating query sets for all cases of project {}.".format(
                    options["project_uuid"]
                )
            except Project.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Project with UUID {options['project_uuid']} not found.")
                )
                sys.exit(0)
            except ValidationError as e:
                self.stderr.write(self.style.ERROR(" ".join(e)))
                sys.exit(0)
        elif options["all"]:
            msg = "Creating query set for all cases."
        else:
            self.stderr.write(self.style.ERROR("Please specify exactly one of the options."))
            sys.exit(0)

        self.stdout.write(self.style.NOTICE(msg))

    def check_result_sets_created(self, count):
        return (
            count["smallvariantqueryresultset"]
            or count["svqueryresultset"]
            or count["sms"]["added"]
            or count["svs"]["added"]
            or count["sms"]["removed"]
            or count["svs"]["removed"]
        )

    def check_annotations_salvable_lost(self, count):
        return (
            count["sms"]["salvable"]["flags"]
            or count["sms"]["salvable"]["comments"]
            or count["sms"]["salvable"]["acmg_ratings"]
            or count["sms"]["lost"]["flags"]
            or count["sms"]["lost"]["comments"]
            or count["sms"]["lost"]["acmg_ratings"]
            or count["svs"]["salvable"]["flags"]
            or count["svs"]["salvable"]["comments"]
            or count["svs"]["lost"]["flags"]
            or count["svs"]["lost"]["comments"]
        )

    def check_salvable(self, count):
        return (
            count["sms"]["salvable"]["flags"]
            or count["sms"]["salvable"]["comments"]
            or count["sms"]["salvable"]["acmg_ratings"]
            or count["svs"]["salvable"]["flags"]
            or count["svs"]["salvable"]["comments"]
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Generate and fill result sets."""
        self.check_arguments(options)
        msg_warning = ""

        if options["async"]:
            count, salvable, duplicates, orphans = create_queryresultset(
                options["case_uuid"], options["project_uuid"], options["all"]
            )
            msg = "Done creating result sets:"
            if self.check_result_sets_created(count):
                msg += MSG_RESULT_SETS_CREATED.format(
                    smallvariantqueryresultset=count["smallvariantqueryresultset"],
                    svqueryresultset=count["svqueryresultset"],
                    sms_added=count["sms"]["added"],
                    svs_added=count["svs"]["added"],
                    sms_removed=count["sms"]["removed"],
                    svs_removed=count["svs"]["removed"],
                )
            else:
                msg += MSG_RESULT_SETS_NOTHING
            if self.check_annotations_salvable_lost(count):
                msg_warning = MSG_RESULT_SETS_WARNING.format(
                    sms_salvable_flags=count["sms"]["salvable"]["flags"],
                    sms_salvable_comments=count["sms"]["salvable"]["comments"],
                    sms_salvable_acmg_ratings=count["sms"]["salvable"]["acmg_ratings"],
                    sms_lost_flags=count["sms"]["lost"]["flags"],
                    sms_lost_comments=count["sms"]["lost"]["comments"],
                    sms_lost_acmg_ratings=count["sms"]["lost"]["acmg_ratings"],
                    svs_salvable_flags=count["svs"]["salvable"]["flags"],
                    svs_salvable_comments=count["svs"]["salvable"]["comments"],
                    svs_lost_flags=count["svs"]["lost"]["flags"],
                    svs_lost_comments=count["svs"]["lost"]["comments"],
                )
            if self.check_salvable(count):
                write_json("salvable.json", salvable)
            if duplicates["sms"] or duplicates["svs"]:
                msg_warning += MSG_DUPLICATES_WARNING.format(
                    duplicates_sms=len(duplicates["sms"]), duplicates_svs=len(duplicates["svs"])
                )
            for i in (
                "sms",
                "svs",
            ):
                if duplicates[i]:
                    write_tsv_simple(
                        f"duplicates_{i}.json",
                        TSV_HEADER_DUPLICATES,
                        TSV_LINE_DUPLICATES,
                        duplicates[i],
                    )
                if orphans[i]["flags"]:
                    write_tsv_flags(
                        f"orphans_{i}_flags.tsv",
                        TSV_HEADER_FLAGS,
                        TSV_LINE_FLAGS,
                        orphans[i]["flags"],
                    )
                if orphans[i]["comments"]:
                    write_tsv_comments(
                        f"orphans_{i}_comments.tsv",
                        TSV_HEADER_COMMENTS,
                        TSV_LINE_COMMENTS,
                        orphans[i]["comments"],
                    )
            if orphans["sms"]["acmg_ratings"]:
                write_tsv_simple(
                    "orphans_sm_acmg_ratings.tsv",
                    TSV_HEADER_SIMPLE,
                    TSV_LINE_SIMPLE,
                    orphans["sms"]["acmg_ratings"],
                )
        else:
            task_create_queryresultset.delay(
                options["case_uuid"], options["project_uuid"], options["all"]
            )
            msg = "Pushed creating the query set to background."

        self.stdout.write(self.style.SUCCESS(msg))
        if msg_warning:
            self.stderr.write(self.style.WARNING(msg_warning))
