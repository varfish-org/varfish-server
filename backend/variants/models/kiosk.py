"""Code for supporting Kiosk mode."""

import contextlib
from datetime import timedelta
import os
import shlex
import shutil
import subprocess
import uuid as uuid_object

from bgjobs.models import LOG_LEVEL_ERROR, LOG_LEVEL_INFO, BackgroundJob, JobModelMessageMixin
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from projectroles.plugins import get_backend_api
from sqlalchemy import delete

from variants.helpers import get_engine
from variants.models.case import Case
from variants.models.maintenance import SiteBgJobBase
from variants.models.projectroles import Project
from variants.models.variants import SmallVariant


class KioskAnnotateBgJob(JobModelMessageMixin, models.Model):
    """Background job for annotating vcf in kiosk mode."""

    #: Task description for logging.
    task_desc = "Kiosk annotate"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.kiosk"

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Job UUID")
    #: The project that the job belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project that is imported to"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
    )

    #: Path to the temporary vcf file.
    path_vcf = models.CharField(
        max_length=4096, blank=False, null=False, help_text="Path to the vcf file to annotate"
    )
    #: Path to the db info file.
    path_db_info = models.CharField(
        max_length=4096, blank=False, null=False, help_text="Output path to the db info file"
    )
    #: Path to the gts variant file.
    path_gts = models.CharField(
        max_length=4096, blank=False, null=False, help_text="Output path to the gts file"
    )
    #: Path to the tmp dir everything is stored.
    path_tmp_dir = models.CharField(
        max_length=4096, blank=False, null=False, help_text="Path to the tmp dir"
    )

    def get_human_readable_type(self):
        return "Annotate small variants in kiosk mode"

    def get_absolute_url(self):
        return reverse(
            "variants:kiosk-annotate-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class KioskAnnotate:
    def __init__(self, job):
        self.job = job

    def run(self):
        """Perform the variant annotation."""
        try:
            process = subprocess.Popen(
                """
                {set_x}
                . {conda_path}
                conda activate varfish-annotator
                set -euo pipefail
                vcf=$(dirname {input_vcf})/sorted-$(basename {input_vcf})
                vcf=${{vcf%.gz}}
                vcf=${{vcf%.vcf}}
                vcf=$vcf.vcf.gz
                bcftools sort -m 10M -Oz -o $vcf {input_vcf}
                tabix -f $vcf
                varfish-annotator \
                    -XX:MaxHeapSize=10g \
                    -XX:+UseConcMarkSweepGC \
                    annotate \
                    --db-path {db_path} \
                    --ensembl-ser-path {ensembl_ser_path} \
                    --refseq-ser-path {refseq_ser_path} \
                    --input-vcf $vcf \
                    --output-db-info >(gzip > {output_db_info}) \
                    --output-gts >(awk -F$'\t' 'BEGIN{{OFS=FS}}{{if(NR>1){{sub(/^chrM/,"MT",$2);sub(/^chr/,"",$2)}}print}}' | gzip > {output_gts}) \
                    --ref-path {reference_path} \
                    --release {release}
                """.format(
                    set_x="set -x" if settings.DEBUG else "",
                    conda_path=settings.KIOSK_CONDA_PATH,
                    db_path=settings.KIOSK_VARFISH_ANNOTATOR_DB_PATH,
                    ensembl_ser_path=settings.KIOSK_VARFISH_ANNOTATOR_ENSEMBL_SER_PATH,
                    refseq_ser_path=settings.KIOSK_VARFISH_ANNOTATOR_REFSEQ_SER_PATH,
                    input_vcf=shlex.quote(self.job.path_vcf),
                    output_db_info=shlex.quote(self.job.path_db_info),
                    output_gts=shlex.quote(self.job.path_gts),
                    reference_path=settings.KIOSK_VARFISH_ANNOTATOR_REFERENCE_PATH,
                    release=settings.KIOSK_VARFISH_ANNOTATOR_RELEASE,
                ),
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,
                shell=True,
                executable="/bin/bash",
            )
            # Get live output from bash job
            while True:
                line = process.stdout.readline()
                if line is not None:
                    self.job.add_log_entry(line.decode("utf-8").strip(), LOG_LEVEL_INFO)
                if process.poll() is not None:
                    while True:
                        line = process.stdout.readline()
                        if line:
                            self.job.add_log_entry(line.decode("utf-8").strip(), LOG_LEVEL_INFO)
                        else:
                            break
                    if not process.poll() == 0:
                        raise subprocess.CalledProcessError(process.poll(), "annotation")
                    break
        except subprocess.CalledProcessError as e:
            self.job.add_log_entry("Problem during kiosk annotation: %s" % e, LOG_LEVEL_ERROR)
            raise e

    def clear(self):
        shutil.rmtree(self.job.path_tmp_dir, ignore_errors=True)
        self.job.add_log_entry("Removing directory %s" % self.job.path_tmp_dir, LOG_LEVEL_INFO)


def run_kiosk_annotate_bg_job(pk):
    timeline = get_backend_api("timeline_backend")
    job = KioskAnnotateBgJob.objects.get(pk=pk)
    started = timezone.now()
    with job.marks():
        KioskAnnotate(job).run()
        if timeline:
            elapsed = timezone.now() - started
            timeline.add_event(
                project=job.project,
                app_name="variants",
                user=job.bg_job.user,
                event_name="kiosk_annotate",
                description='Annotation of VCF file "%s" finished in %.2fs.'
                % (os.path.basename(job.path_vcf), elapsed.total_seconds()),
                status_type="OK",
            )


def run_clear_kiosk_bg_job(pk):
    job = KioskAnnotateBgJob.objects.get(pk=pk)
    KioskAnnotate(job).clear()


def clear_old_kiosk_cases():
    """Clear out cases that are older than a week."""

    # Do nothing if kiosk mode isn't enabled.
    if not settings.KIOSK_MODE:
        return

    # Find the correct category
    cat = Project.objects.get(type="CATEGORY", title=settings.KIOSK_CAT)
    # Define allowed period (~2 months)
    time_threshold = timezone.now() - timedelta(weeks=8)
    # Find the correct project within the category and within cases that are older than threshold
    cases = Case.objects.filter(
        project__type="PROJECT", project__parent_id=cat.id, date_created__lte=time_threshold
    )
    projects = []
    # Delete cases and associated variants
    for case in cases:
        projects.append(case.project)
        # Delete all small variants.
        with contextlib.closing(
            get_engine().execute(
                delete(SmallVariant.sa.table).where(SmallVariant.sa.case_id == case.id)
            )
        ):
            pass
        # Delete case
        case.delete()
    # Delete projects as every case has its own project and is not required anymore
    for project in set(projects):
        project.delete()


class ClearOldKioskCasesBgJob(SiteBgJobBase):
    """Background job for clearing old Kiosk cases."""

    #: Task description for logging.
    task_desc = "Clearing old (and expired) Varfish Kiosk cases"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.clear_old_kiosk_cases_bg_job"

    def get_absolute_url(self):
        return reverse(
            "variants:clear-old-kiosk-cases-job-detail",
            kwargs={"job": self.sodar_uuid},
        )
