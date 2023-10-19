"""Django command for generating query result sets."""
import json

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from projectroles.models import Project

from variants.models import Case
from variants.tasks import create_queryresultset as task_create_queryresultset
from variants.utils import create_queryresultset


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

    @transaction.atomic
    def handle(self, *args, **options):
        """Perform rebuilding the statistics."""
        if bool(options["case_uuid"]) + bool(options["project_uuid"]) + bool(options["all"]) != 1:
            self.stderr.write(self.style.ERROR("Please specify exactly one of the options."))
            return

        if options["case_uuid"]:
            try:
                Case.objects.get(sodar_uuid=options["case_uuid"])
                msg = "Creating query set for case {}.".format(options["case_uuid"])
            except Case.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Case with UUID {options['case_uuid']} not found.")
                )
                return
            except ValidationError as e:
                self.stderr.write(self.style.ERROR(" ".join(e)))
                return
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
                return
            except ValidationError as e:
                self.stderr.write(self.style.ERROR(" ".join(e)))
                return
        else:
            msg = "Creating query set for all cases."

        self.stdout.write(self.style.NOTICE(msg))
        msg_warning = ""

        if options["async"]:
            count, salvable, duplicates, orphans = create_queryresultset(
                options["case_uuid"], options["project_uuid"], options["all"]
            )
            msg = "Done creating result sets:"
            if (
                count["smallvariantqueryresultset"]
                or count["svqueryresultset"]
                or count["sms"]["added"]
                or count["svs"]["added"]
                or count["sms"]["removed"]
                or count["svs"]["removed"]
            ):
                msg += f"""
- SmallVariantQueryResultSets created: {count['smallvariantqueryresultset']}
- SvQueryResultSets created: {count['svqueryresultset']}
- SmallVariantQueryResultSets:
  - Added: {count['sms']['added']}
  - Removed: {count['sms']['removed']}
- SvQueryResultSets:
  - Added: {count['svs']['added']}
  - Removed: {count['svs']['removed']}"""
            else:
                msg += "\n- Nothing to do."
            if (
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
            ):
                msg_warning = f"""
WARNING! There are orphaned annotations:
- SmallVariant annotations:
  - Salvable:
    - Flags: {count['sms']['salvable']['flags']}
    - Comments: {count['sms']['salvable']['comments']}
    - ACMG ratings: {count['sms']['salvable']['acmg_ratings']}
  - Lost:
    - Flags: {count['sms']['lost']['flags']}
    - Comments: {count['sms']['lost']['comments']}
    - ACMG ratings: {count['sms']['lost']['acmg_ratings']}
- StructuralVariant annotations:
  - Salvable:
    - Flags: {count['svs']['salvable']['flags']}
    - Comments: {count['svs']['salvable']['comments']}
  - Lost:
    - Flags: {count['svs']['lost']['flags']}
    - Comments: {count['svs']['lost']['comments']}""".lstrip()
            if (
                count["sms"]["salvable"]["flags"]
                or count["sms"]["salvable"]["comments"]
                or count["sms"]["salvable"]["acmg_ratings"]
                or count["svs"]["salvable"]["flags"]
                or count["svs"]["salvable"]["comments"]
            ):
                with open("salvable.json", "w") as f:
                    json.dump(salvable, f, indent=1)
            if duplicates["sms"] or duplicates["svs"]:
                msg_warning += f"""
WARNING! There are duplicate variants:
- Duplicate small variants: {len(duplicates['sms'])}
- Duplicate structural variants: {len(duplicates['svs'])}""".lstrip()
            if duplicates["sms"]:
                with open("duplicates_sms.json", "w") as f:
                    f.write("case_uuid\tproject\tcase_name\tregion\tjson\n")
                    for line in duplicates["sms"]:
                        f.write(
                            "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{json}\n".format(
                                **line,
                            )
                        )
            if duplicates["svs"]:
                with open("duplicates_svs.json", "w") as f:
                    f.write("case_uuid\tproject\tcase_name\tregion\tjson\n")
                    for line in duplicates["svs"]:
                        f.write(
                            "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{json}\n".format(
                                **line,
                            )
                        )
            if orphans["svs"]["flags"]:
                with open("orphans_sv_flags.tsv", "w") as f:
                    f.write(
                        "case_uuid\tproject\tcase_name\tregion\tlost\tflag_molecular\tflag_visual\tflag_validation\tflag_phenotype_match\tflag_summary\tjson\n"
                    )
                    for line in orphans["svs"]["flags"]:
                        j = json.loads(line["json"])
                        f.write(
                            "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{lost}\t{flag_molecular}\t{flag_visual}\t{flag_validation}\t{flag_phenotype_match}\t{flag_summary}\t{json}\n".format(
                                **line,
                                flag_molecular=j["flag_molecular"],
                                flag_visual=j["flag_visual"],
                                flag_validation=j["flag_validation"],
                                flag_phenotype_match=j["flag_phenotype_match"],
                                flag_summary=j["flag_summary"],
                            )
                        )
            if orphans["svs"]["comments"]:
                with open("orphans_sv_comments.tsv", "w") as f:
                    f.write("case_uuid\tproject\tcase_name\tregion\tlost\tcomment\tjson\n")
                    for line in orphans["svs"]["comments"]:
                        j = json.loads(line["json"])
                        f.write(
                            "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{lost}\t{comment}\t{json}\n".format(
                                **line,
                                comment=j["text"],
                            )
                        )
            if orphans["sms"]["flags"]:
                with open("orphans_sm_flags.tsv", "w") as f:
                    f.write(
                        "case_uuid\tproject\tcase_name\tregion\tlost\tflag_molecular\tflag_visual\tflag_validation\tflag_phenotype_match\tflag_summary\tjson\n"
                    )
                    for line in orphans["sms"]["flags"]:
                        j = json.loads(line["json"])
                        f.write(
                            "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{lost}\t{flag_molecular}\t{flag_visual}\t{flag_validation}\t{flag_phenotype_match}\t{flag_summary}\t{json}\n".format(
                                **line,
                                flag_molecular=j["flag_molecular"],
                                flag_visual=j["flag_visual"],
                                flag_validation=j["flag_validation"],
                                flag_phenotype_match=j["flag_phenotype_match"],
                                flag_summary=j["flag_summary"],
                            )
                        )
            if orphans["sms"]["comments"]:
                with open("orphans_sm_comments.tsv", "w") as f:
                    f.write("case_uuid\tproject\tcase_name\tregion\tlost\tcomment\tjson\n")
                    for line in orphans["sms"]["comments"]:
                        j = json.loads(line["json"])
                        f.write(
                            "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{lost}\t{comment}\t{json}\n".format(
                                **line,
                                comment=j["text"],
                            )
                        )
            if orphans["sms"]["acmg_ratings"]:
                with open("orphans_sm_acmg_ratings.tsv", "w") as f:
                    f.write("case_uuid\tproject\tcase_name\tregion\tlost\tjson\n")
                    for line in orphans["sms"]["acmg_ratings"]:
                        f.write(
                            "{case_uuid}\t{project}\t{case_name}\t{chromosome}:{start}-{end}\t{lost}\t{json}\n".format(
                                **line
                            )
                        )
        else:
            task_create_queryresultset.delay(
                options["case_uuid"], options["project_uuid"], options["all"]
            )
            msg = "Pushed creating the query set to background."

        self.stdout.write(self.style.SUCCESS(msg))
        if msg_warning:
            self.stderr.write(self.style.WARNING(msg_warning))
