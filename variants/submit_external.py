"""This module contains the code for file export"""
import gzip
import re

from bs4 import BeautifulSoup
from projectroles.plugins import get_backend_api
import requests

from .file_export import CaseExporterVcf

#: URL to MutationDistiller submission form
DISTILLER_POST_URL = "https://www.mutationdistiller.org/QE/MT/MTQE_start.cgi"


def submit_distiller(job):
    """Submit a case to MutationDistiller"""
    job.mark_start()
    timeline = get_backend_api("timeline_backend")
    if timeline:
        tl_event = timeline.add_event(
            project=job.project,
            app_name="variants",
            user=job.bg_job.user,
            event_name="case_submit_distiller",
            description="submitting {case_name} case to MutationDistiller",
            status_type="INIT",
        )
        tl_event.add_object(obj=job.case, label="case_name", name=job.case.name)
    try:
        data = {
            "name": "%(name)s (sodar:%(project)s varfish:%(case)s)"
            % {
                "name": job.case.name,
                "project": job.project.sodar_uuid,
                "case": job.case.sodar_uuid,
            }
        }
        if job.bg_job.user.email:
            data["email"] = job.bg_job.user.email
        with CaseExporterVcf(job, job.case) as exporter:
            job.add_log_entry("Creating temporary VCF file...")
            files = {"filename": exporter.write_tmp_file()}
            job.add_log_entry("Done creating temporary VCF file.")
            job.add_log_entry("Submitting to MutationDistiller.org...")
            response = requests.post(DISTILLER_POST_URL, data=data, files=files)
            job.add_log_entry("Done submitting to MutationDistiller.org")
        if not response.ok:
            job.mark_error("HTTP status code: {}".format(response.status_code))
            if timeline:
                tl_event.set_status("FAILED", "MutationDistiller submission failed for {case_name}")
            return  # bail out!
        # Get ID in MutationDistiller
        job.add_log_entry("Parsing MutationDistiller response...")
        distiller_id = None
        soup = BeautifulSoup(response.text, "html.parser")
        for meta in soup.find_all("meta"):
            if meta.attrs.get("http-equiv") == "refresh":
                url = meta.attrs.get("content").split("=")[-1]
                job.add_log_entry("URL = {}".format(url))
                m = re.match(r"/temp/QE/vcf_([^/]+)/progress.html", url)
                if m:
                    distiller_id = m.group(1)
                job.add_log_entry("Distiller ID = {}".format(distiller_id))
        if not distiller_id:
            job.mark_error("Could not find MutationDistiller ID from response")
            if timeline:
                tl_event.set_status("FAILED", "Could not find MutationDistiller ID from response")
            return  # bail out!
        job.distiller_project_id = distiller_id
        job.save()
    except Exception as e:
        job.mark_error(e)
        if timeline:
            tl_event.set_status("FAILED", "MutationDistiller submission failed for {case_name}: %s")
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status("OK", "MutationDistiller submission complete for {case_name}")


#: URL to CADD submission form
CADD_POST_URL = "https://cadd.gs.washington.edu/upload"


def submit_cadd(job):
    """Submit a case to CADD"""
    job.mark_start()
    timeline = get_backend_api("timeline_backend")
    if timeline:
        tl_event = timeline.add_event(
            project=job.project,
            app_name="variants",
            user=job.bg_job.user,
            event_name="case_submit_cadd",
            description="submitting {case_name} case to CADD",
            status_type="INIT",
        )
        tl_event.add_object(obj=job.case, label="case_name", name=job.case.name)
    try:
        data = {
            "version": job.cadd_version,
            "inclAnno": "Yes",
            "submit": "Upload variants",
        }
        with CaseExporterVcf(job, job.case) as exporter:
            job.add_log_entry("Creating temporary VCF file...")
            files = {"file": exporter.write_tmp_file()}
            job.add_log_entry("Done creating temporary VCF file.")
            job.add_log_entry("Submitting to %s ..." % CADD_POST_URL)
            response = requests.post(CADD_POST_URL, data=data, files=files)
            job.add_log_entry("Done submitting to %s" % CADD_POST_URL)
        if not response.ok:
            job.mark_error("HTTP status code: {}".format(response.status_code))
            if timeline:
                tl_event.set_status("FAILED", "CADD submission failed for {case_name}")
            return  # bail out!
        # Get ID in CADD
        job.add_log_entry("Parsing CADD response...")
        cadd_job_id = None
        soup = BeautifulSoup(response.text, "html.parser")
        for anchor in soup.find_all("a"):
            if anchor.attrs.get("href").startswith(("/check_avail", "/static/finished")):
                href = anchor.attrs.get("href")
                cadd_job_id = re.split(r"[_.]", href)[-3]
                job.add_log_entry("CADD result ID = {}".format(cadd_job_id))
                break
        if not cadd_job_id:
            job.mark_error("Could not find CADD result ID from response")
            if timeline:
                tl_event.set_status("FAILED", "Could not find CADD result ID from response")
            return  # bail out!
        job.cadd_job_id = cadd_job_id
        job.save()
    except Exception as e:
        job.mark_error(e)
        if timeline:
            tl_event.set_status("FAILED", "CADD submission failed for {case_name}: %s")
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status("OK", "CADD submission complete for {case_name}")


#: URL to SPANR submission form
SPANR_POST_URL = "http://tools.genes.toronto.edu/"
#: Maximum number of lines to write out
SPANR_MAX_LINES = 40


def submit_spanr(job):
    """Submit a case to SPANR."""
    job.mark_start()
    timeline = get_backend_api("timeline_backend")
    if timeline:
        tl_event = timeline.add_event(
            project=job.project,
            app_name="variants",
            user=job.bg_job.user,
            event_name="case_submit_spanr",
            description="submitting {case_name} case to SPANR",
            status_type="INIT",
        )
        tl_event.add_object(obj=job.case, label="case_name", name=job.case.name)
    try:
        job.add_log_entry("Getting submission form for CSRF (security) token")
        text_input = _submit_spanr_make_text(job)
        job.add_log_entry("Getting submission form for CSRF (security) token")
        session = requests.Session()
        csrf_token = _submit_spanr_obtain_csrf_token(job, session, timeline, tl_event)
        if not csrf_token:
            return  # bail out!
        data = {"csrf_token": (None, csrf_token), "text_input": (None, text_input)}
        job_id = _submit_spanr_post(data, job, session, timeline, tl_event)
        if not job_id:
            return  # bail out!
        # Get target URL
        job.spanr_job_url = "%sresults/%s" % (SPANR_POST_URL, job_id)
        job.add_log_entry("SPANR job page is %s" % job.spanr_job_url)
        job.save()
    except Exception as e:
        job.mark_error(e)
        if timeline:
            tl_event.set_status("FAILED", "SPANR submission failed for {case_name}: %s")
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status("OK", "SPANR submission complete for {case_name}")


def _submit_spanr_post(data, job, session, timeline, tl_event):
    job.add_log_entry("Submitting to %s..." % SPANR_POST_URL)
    for k in ("job_name", "chrom", "pos", "variant_id", "ref", "alt"):
        data[k] = (None, "")
    response = session.post(
        SPANR_POST_URL,
        files=data,
        headers={
            "Referer": SPANR_POST_URL,
            "Origin": SPANR_POST_URL[:-1],
            "Upgrade-Insecure-Requests": "1",
        },
    )
    job.add_log_entry("Done submitting to %s" % SPANR_POST_URL)
    if not response.ok:
        job.mark_error("HTTP status code: {}".format(response.status_code))
        if timeline:
            tl_event.set_status("FAILED", "SPANR submission failed for {case_name}")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    job_id = None
    for tag in soup.find_all("title"):
        text = tag.string
        if text.startswith("Result"):
            job_id = text.split()[1]
    if not job_id:
        job.mark_error('Page title did not start with "Result"')
        if timeline:
            tl_event.set_status("FAILED", "SPANR submission failed for {case_name}")
    return job_id


def _submit_spanr_make_text(job):
    with CaseExporterVcf(job, job.case) as exporter:
        job.add_log_entry("Creating temporary VCF file...")
        tmp_file = exporter.write_tmp_file()
        job.add_log_entry("Extracting first 40 variants...")
        lines = []
        with gzip.open(tmp_file.name, "rt") as inputf:
            i = 0
            for line in inputf:
                if not line.startswith("#"):
                    lines.append("\t".join(line.split("\t")[:5]))
                i += 1
                if i >= SPANR_MAX_LINES:
                    break
        text_input = "\n".join(lines) + "\n"
    return text_input


def _submit_spanr_obtain_csrf_token(job, session, timeline, tl_event):
    response = session.get(SPANR_POST_URL)
    if not response.ok:
        job.mark_error("HTTP status code: {}".format(response.status_code))
        if timeline:
            tl_event.set_status("FAILED", "SPANR submission failed for {case_name}")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    tag = soup.find(id="csrf_token")
    if not tag:
        job.mark_error("Could not extract CSRF token")
        if timeline:
            tl_event.set_status("FAILED", "SPANR submission failed for {case_name}")
        return None
    return tag.attrs.get("value")
