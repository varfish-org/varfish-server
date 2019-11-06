"""Code for synchronizing with upstream SODAR."""

import typing

from django.db import transaction
from bgjobs.models import LOG_LEVEL_ERROR, LOG_LEVEL_WARNING
from projectroles.plugins import get_backend_api
from projectroles.models import RemoteSite
import requests
import attr

from variants.models import CaseAwareProject, SyncCaseResultMessage

URL_TEMPLATE = "%(url)s/samplesheets/api/remote/get/%(project_uuid)s/%(secret)s"


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


def process_json(all_data, add_log_entry):
    """Process the JSON data from upstream SODAR project."""
    # add_log_entry(all_data)
    if len(all_data["studies"]) > 1:
        raise Exception("More than one study found!")

    # Parse out study data.
    study = list(all_data["studies"].values())[0]
    study_infos = study["study"]
    study_top = study_infos["top_header"]
    n_source = study_top[0]["colspan"]
    n_extraction = study_top[1]["colspan"]
    n_sample = study_top[2]["colspan"]
    cols_source = study_infos["field_header"][:n_source]
    cols_extraction = study_infos["field_header"][n_source : n_source + n_extraction]
    cols_sample = study_infos["field_header"][n_source + n_extraction :]
    names_source = [x["value"] for x in cols_source]
    names_extraction = [x["value"] for x in cols_extraction]
    names_sample = [x["value"] for x in cols_sample]
    table = study_infos["table_data"]

    def strip(x):
        if hasattr(x, "strip"):
            return x.strip()
        else:
            return x

    # Build study info map.
    study_map = {}
    for row in table:
        # Assign fields to table.
        dict_source = dict(zip(names_source, [strip(x["value"]) for x in row[:n_source]]))
        dict_extraction = dict(
            zip(
                names_extraction,
                [strip(x["value"]) for x in row[n_source : n_source + n_extraction]],
            )
        )
        dict_sample = dict(
            zip(names_sample, [strip(x["value"]) for x in row[n_source + n_extraction :]])
        )
        # Extend study_map.
        study_map[dict_source["Name"]] = {
            "Source": dict_source,
            "Extraction": dict_extraction,
            "Sample": dict_sample,
        }

    # Parse out the assay data.
    #
    # NB: We're not completely cleanly decomposing the information and, e.g., overwrite
    # the "Extract name" keys here...
    if len(study["assays"]) > 1:
        raise Exception("More than one assay found!")
    assay = list(study["assays"].values())[0]
    top_columns = [(x["value"], x["colspan"]) for x in assay["top_header"]]
    columns = []
    offset = 0
    for type_, colspan in top_columns:
        columns.append(
            {
                "type": type_,
                "columns": [x["value"] for x in assay["field_header"][offset : offset + colspan]],
            }
        )
        offset += colspan
    assay_map = {}
    for row in assay["table_data"]:
        offset = 0
        name = row[0]["value"]
        for column in columns:
            values = {
                "type": column["type"],
                **dict(
                    zip(column["columns"], [x["value"] for x in row[offset : offset + colspan]])
                ),
            }
            type_ = column["type"]
            if type_ == "Process":
                type_ = values["Protocol"]
            assay_map.setdefault(name, {})[type_] = values
            colspan = len(column["columns"])
            offset += colspan

    # add_log_entry("study_map %s" % study_map)
    # add_log_entry("assay_map %s" % assay_map)

    # Generate the resulting sample sheet.
    for source, info in study_map.items():
        if not source in assay_map:
            dict_lib = {"Name": "-.1", "Folder Name": ".", "Batch": "."}  # HAAACKY
        else:
            dict_lib = assay_map[source]["Extract Name"]
        dict_source = info["Source"]
        yield {
            "source_name": dict_source["Name"],
            "father": dict_source["Father"],
            "mother": dict_source["Mother"],
            "sex": dict_source["Sex"],
            "family": dict_source["Family"],
            "affected": dict_source["Disease Status"],
            "sample_name": dict_lib["Name"],
        }


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
        else:
            source = sources[0]
        project = CaseAwareProject.objects.get(pk=job.project.pk)
        r = requests.get(
            URL_TEMPLATE
            % {"url": source.url, "project_uuid": project.sodar_uuid, "secret": source.secret}
        )

        upstream_pedigree = {
            entry["source_name"]: PedigreeMember(
                family=entry["family"],
                name=entry["source_name"],
                father=entry["father"],
                mother=entry["mother"],
                sex=MAPPING_SEX.get(entry["sex"], 0),
                affected=MAPPING_STATUS.get(entry["affected"], 0),
                sample_name=entry["sample_name"],
            )
            for entry in process_json(r.json(), job.add_log_entry)
        }

        compare_to_upstream(project, upstream_pedigree, job)
    except Exception as e:
        job.mark_error(e)
        if timeline:
            tl_event.set_status("FAILED", "syncing with upstream SODAR failed")
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status("OK", "syncing with upstream SODAR successful")
