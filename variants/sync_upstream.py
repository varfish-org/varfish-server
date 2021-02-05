"""Code for synchronizing with upstream SODAR."""

import io
import typing

import attr
from altamisa.isatab import StudyReader
from django.db import transaction
from bgjobs.models import LOG_LEVEL_ERROR, LOG_LEVEL_WARNING
from projectroles.plugins import get_backend_api
from projectroles.models import RemoteSite
import requests

from variants.models import CaseAwareProject, SyncCaseResultMessage

URL_TEMPLATE = "%(url)s/samplesheets/api/remote/get/%(project_uuid)s/%(secret)s?isa=1"


#: Mapping from ISA-tab sex to PED sex.
MAPPING_SEX = {"female": 2, "male": 1, "unknown": 0, None: 0}

#: Mapping from disease status to PED disease status.
MAPPING_STATUS = {"affected": 2, "carrier": 1, "unaffected": 1, "unknown": 0, None: 0}


@attr.s(frozen=True, auto_attribs=True)
class PedigreeMember:
    family: typing.Optional[str]
    name: str
    father: str
    mother: str
    sex: int
    affected: int
    sample_name: str


def compare_to_upstream(project, upstream_pedigree, job):
    """Compare the VarFish project to the pedigree created from upstream SODAR site.

    ``job`` is used for logging.
    """
    local_pedigree = {}
    for line in project.pedigree():
        local_pedigree[line["patient"].split("-")[0]] = PedigreeMember(
            family=None,
            name=line["patient"].split("-")[0],
            father=line["father"].split("-")[0],
            mother=line["mother"].split("-")[0],
            sex=line["sex"],
            affected=line["affected"],
            sample_name=line["patient"],
        )

    local_families = set()
    for line in project.pedigree():
        if "family" in line:
            local_families.add(line["family"])
    upstream_families = set()
    for member in upstream_pedigree.values():
        if member.family:
            upstream_families.add(member.family)

    with transaction.atomic():
        # Clear out old messages.
        SyncCaseResultMessage.objects.filter(project=project).delete()
        # All upstream donors in local project?
        local_missing = set(upstream_pedigree.keys()) - set(local_pedigree.keys())
        if local_missing:
            tpl = "Upstream/SODAR donors not found in VarFish project: %s."
            project.synccaseresultmessage_set.create(
                level=LOG_LEVEL_ERROR, message=tpl % ", ".join(sorted(local_missing))
            )
            job.add_log_entry(tpl % ", ".join(sorted(local_missing)))
        # All local donors in upstream pedigree?
        upstream_missing = set(local_pedigree.keys()) - set(upstream_pedigree.keys())
        if upstream_missing:
            tpl = "Varfish project donors not found in upstream/SODAR: %s."
            project.synccaseresultmessage_set.create(
                level=LOG_LEVEL_ERROR, message=tpl % ", ".join(sorted(upstream_missing))
            )
            job.add_log_entry(tpl % ", ".join(sorted(upstream_missing)))
        # All upstream families in local project?
        if (
            local_families
        ):  # TODO: families not assigned by default now, remove this condition once it is
            local_missing = upstream_families - local_families
            if local_missing:
                tpl = "Upstream/SODAR donors not found in VarFish project: %s."
                project.synccaseresultmessage_set.create(
                    level=LOG_LEVEL_ERROR, message=tpl % ", ".join(sorted(local_missing))
                )
                job.add_log_entry(tpl % ", ".join(sorted(local_missing)))
        # All local families in upstream pedigree?
        upstream_missing = local_families - upstream_families
        if upstream_missing:
            tpl = "Varfish project families not found in upstream/SODAR: %s."
            project.synccaseresultmessage_set.create(
                level=LOG_LEVEL_ERROR, message=tpl % ", ".join(sorted(upstream_missing))
            )
            job.add_log_entry(tpl % ", ".join(sorted(upstream_missing)))
        # Do sex and affection status and parents match?
        for name in sorted(set(local_pedigree.keys()) & set(upstream_pedigree.keys())):
            local = local_pedigree[name]
            upstream = upstream_pedigree[name]
            for key, title in (
                ("sex", "Sex"),
                ("affected", "Disease status"),
                ("father", "Father"),
                ("mother", "Mother"),
            ):
                if getattr(local, key) != getattr(upstream, key):
                    tpl = "%s does not match for %s between local project and upstream."
                    project.synccaseresultmessage_set.create(
                        level=LOG_LEVEL_WARNING, message=tpl % (title, name)
                    )
                    job.add_log_entry(tpl % (title, name))


def _nolog(msg, log_level=None):
    """Helper log function that does not do anything."""
    _, _ = msg, log_level


def _isa_helper_get_field(fields, key):
    """Helper for easily obtaining value from an ISA-tab field."""
    return ";".join(fields.get(key, ()))


def fetch_remote_pedigree(source, project, add_log_entry=_nolog):
    """Fetch pedigree (dict of ``PedigreeMember``) from remote site ``source``."""
    r = requests.get(
        URL_TEMPLATE
        % {"url": source.url, "project_uuid": project.sodar_uuid, "secret": source.secret}
    )

    # Mapping from sex in ISA-tab to sex in PLINK PED.
    map_sex = {"male": 1, "female": 2}
    # Mapping from disease state in ISA-tab to sex in PLINK PED.
    map_affected = {"affected": 2, "unaffected": 1}

    # Parse investigation and all studies from ISA-tab (wrapped in JSON).
    remote_pedigree = {}
    isa_json = r.json()

    for s_path, s_data in isa_json["studies"].items():
        study = StudyReader.from_stream(s_path, io.StringIO(s_data["tsv"]), filename=s_path).read()
        add_log_entry(study)
        # Compress study arcs (map source to sample), easy because only one depth of one in study.
        arc_map = {arc.tail: arc for arc in study.arcs}
        for arc in list(arc_map.values()):  # NB: copy intentionally
            if arc.head in arc_map:
                arc_map[arc.tail] = arc_map[arc.head]
        add_log_entry(arc_map)
        # Actually parse out individuals.
        source_samples = {}
        for arc in study.arcs:
            if arc.tail in study.materials and study.materials[arc.tail].type == "Source Name":
                source_samples.setdefault(arc.tail, []).append(
                    study.materials[arc_map[arc.tail].head]
                )
        for material in study.materials.values():
            if material.type == "Source Name":
                if len(source_samples[material.unique_name]) > 1:
                    add_log_entry(
                        "WARNING: more than one sample for source %s" % material.name,
                        log_level=LOG_LEVEL_WARNING,
                    )
                fields = {c.name: c.value for c in material.characteristics}
                add_log_entry("fields = %s" % fields)
                member = PedigreeMember(
                    family=_isa_helper_get_field(fields, "Family"),
                    name=material.name,
                    father=_isa_helper_get_field(fields, "Father"),
                    mother=_isa_helper_get_field(fields, "Mother"),
                    sex=map_sex.get(_isa_helper_get_field(fields, "Sex"), 0),
                    affected=map_affected.get(_isa_helper_get_field(fields, "Disease status"), 0),
                    sample_name=source_samples[material.unique_name][0].name,
                )
                add_log_entry("new member: %s" % member)
                remote_pedigree[material.name] = member

    return remote_pedigree


def execute_sync_case_list_job(job):
    """Synchronise cases within a project with the upstream SODAR site."""
    job.mark_start()
    timeline = get_backend_api("timeline_backend")
    if timeline:
        tl_event = timeline.add_event(
            project=job.project,
            app_name="variants",
            user=job.bg_job.user,
            event_name="project_sync_upstream",
            description="sychronising with upstream SODAR",
            status_type="INIT",
        )
    try:
        sources = [s for s in RemoteSite.objects.all() if s.mode == "SOURCE"]
        if len(sources) != 1:
            raise RuntimeError(
                "Expected exactly one remote source site but there were %d" % len(sources)
            )

        project = CaseAwareProject.objects.get(pk=job.project.pk)
        upstream_pedigree = fetch_remote_pedigree(sources[0], project, job.bg_job.add_log_entry)
        compare_to_upstream(project, upstream_pedigree, job)
    except Exception as e:
        job.mark_error("%s: %s" % (type(e).__name__, e))
        if timeline:
            tl_event.set_status("FAILED", "syncing with upstream SODAR failed")
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status("OK", "syncing with upstream SODAR successful")
