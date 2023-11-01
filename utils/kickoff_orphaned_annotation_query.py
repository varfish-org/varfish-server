import json
import os
import sys
import time

import requests
import toml

#: Paths to search the global configuration in.
GLOBAL_CONFIG_PATHS = ("~/.varfishrc.toml",)

#: Endpoint to smallvariant query settings
ENDPOINT_SM_SETTINGS = (
    "/variants/api/query-case/query-settings-shortcut/{case_uuid}?quick_preset=whole_exome"
)
#: Endpoint to smallvariant list-create query
ENDPOINT_SM_LISTCREATE_QUERY = "/variants/api/query/list-create/{case_uuid}"
#: Endpoint to smallvariant retrieve query
ENDPOINT_SM_RETRIEVE_QUERY = "/svs/api/query/retrieve-update-destroy/{query_uuid}/"
#: Endpoint to structuralvariant query settings
ENDPOINT_SV_SETTINGS = "/svs/ajax/query-case/query-settings-shortcut/{case_uuid}/?quick_preset=whole_genome&genotype_criteria=default&inheritance=any&frequency=any&impact=any&sv_type=any"
#: Endpoint to structuralvariant list-create query
ENDPOINT_SV_LISTCREATE_QUERY = "/svs/ajax/sv-query/list-create/{case_uuid}/"
#: Endpoint to structuralvariant retrieve query
ENDPOINT_SV_RETRIEVE_QUERY = "/svs/ajax/sv-query/retrieve-update-destroy/{query_uuid}/"

#: Sleep time between starting queries
SLEEP_RUN = 2
#: Sleep time between polling queries
SLEEP_POLL = 5

#: SQL database name for structural variants
SQL_SV_DB = "svs_structuralvariant"
#: SQL database name for small variants
SQL_SM_DB = "variants_smallvariant"
#: SQL query template to retrieve variants
SQL_QUERY_TEMPLATE = "select * from {db} left outer join variants_case on variants_case.id={db}.case_id where variants_case.sodar_uuid='{case_uuid}' and {db}.release='GRCh37' and chromosome='{chromosome}' and start={start};\n"


def connect_endpoint(config, endpoint, data=None):
    token = config.get("global", {}).get("varfish_api_token")
    base = config.get("global", {}).get("varfish_server_url").rstrip("/")
    url = f"{base}{endpoint}"
    headers = {"Authorization": f"Token {token}"}
    if data:
        response = requests.post(url, headers=headers, json=data)
    else:
        response = requests.get(url, headers=headers)
    if response.status_code not in (
        200,
        201,
    ):
        sys.stderr.write(f"Error: {url} responded with {response.status_code}\n")
        return {}
    return response


def read_json(file):
    with open(file, "r") as f:
        return json.load(f)


def read_toml():
    for config_path in GLOBAL_CONFIG_PATHS:
        config_path = os.path.expanduser(os.path.expandvars(config_path))
        if os.path.exists(config_path):
            with open(config_path, "rt") as tomlf:
                return toml.load(tomlf)
    else:
        sys.stderr.write(
            f"Could not find any of the global configuration files {GLOBAL_CONFIG_PATHS}"
        )
        sys.exit()


def run_query(config, settings_endpoint, query_endpoint, case_uuid, case_orphans, log_line):
    url = settings_endpoint.format(case_uuid=case_uuid)
    response = connect_endpoint(config, url)
    if not response:
        return ""
    response_json = response.json()
    response_json["query_settings"]["genomic_region"] = case_orphans
    if "genotype_criteria" in response_json["query_settings"]:
        for criteria in response_json["query_settings"]["genotype_criteria"]:
            criteria["gt_one_of"].append(".")
            criteria["gt_one_of"].append("./.")
    url = query_endpoint.format(case_uuid=case_uuid)
    response = connect_endpoint(config, url, data=response_json)
    if not response:
        return ""
    sys.stdout.write(log_line.format(case_uuid=case_uuid, len_case_orphans=len(case_orphans)))
    response_json = response.json()
    if not response_json.get("sodar_uuid"):
        sys.stderr.write(f"Error: got no query uuid for case {case_uuid}\n")
        return ""
    time.sleep(SLEEP_RUN)
    return response_json["sodar_uuid"]


def poll_query(config, query_endpoint, query_uuid):
    url = query_endpoint.format(query_uuid=query_uuid)
    response = connect_endpoint(config, url)
    if not response:
        return {"query_state": "fetching_failed"}
    return response.json()


def poll_queries(config, query_endpoint, query_uuids):
    poll_running = []
    for query_uuid, data in query_uuids.items():
        if not data["running"]:
            continue
        query_data = poll_query(config, query_endpoint, query_uuid)
        data["state"] = query_data["query_state"]
        data["logs"] = query_data["logs"]
        data["running"] = query_data["query_state"] == "running"
        poll_running.append(data["running"])
    return any(poll_running)


def main():
    orphans = read_json(sys.argv[1])
    config = read_toml()
    query_results = {"svs": {}, "sms": {}}
    sys.stdout.write("Starting queries ...\n")
    log_line_success = "query created for case {case_uuid}, {len_case_orphans} orphans\n"
    for case_uuid, case_orphans in orphans.items():
        if case_orphans["sms"]:
            query_uuid = run_query(
                config,
                ENDPOINT_SM_SETTINGS,
                ENDPOINT_SM_LISTCREATE_QUERY,
                case_uuid,
                case_orphans["sms"],
                f"Small variant {log_line_success}",
            )
            if not query_uuid:
                continue
            query_results["sms"][query_uuid] = {
                "running": True,
                "state": "initial",
                "case_uuid": case_uuid,
                "orphans": case_orphans["sms"],
                "logs": [],
            }
        if case_orphans["svs"]:
            query_uuid = run_query(
                config,
                ENDPOINT_SV_SETTINGS,
                ENDPOINT_SV_LISTCREATE_QUERY,
                case_uuid,
                case_orphans["svs"],
                f"Structural variant {log_line_success}",
            )
            if not query_uuid:
                continue
            query_results["svs"][query_uuid] = {
                "running": True,
                "state": "initial",
                "case_uuid": case_uuid,
                "orphans": case_orphans["svs"],
                "logs": [],
            }
    sys.stdout.write("Done starting queries!\n")
    while True:
        sys.stdout.write("Waiting for queries to finish ...\n")
        sm_polls_running = poll_queries(config, ENDPOINT_SM_RETRIEVE_QUERY, query_results["sms"])
        sv_polls_running = poll_queries(config, ENDPOINT_SV_RETRIEVE_QUERY, query_results["svs"])
        if not sm_polls_running and not sv_polls_running:
            break
        time.sleep(SLEEP_POLL)
    sys.stdout.write("Writing out json dump ...\n")
    with open("query_results.json", "w") as fh:
        json.dump(query_results, fh, indent=1)
    sys.stdout.write("Writing out SQL queries for small variants ...\n")
    with open("query_results_sm.tsv", "w") as fh:
        fh.write("case_uuid\tcoords\tquery\n")
        for query_uuid, query_result in query_results["sms"].items():
            for coords in query_result["orphans"]:
                chromosome, start_end = coords.split(":")
                start, end = start_end.split("-")
                fh.write(
                    SQL_QUERY_TEMPLATE.format(
                        db=SQL_SM_DB,
                        case_uuid=query_result["case_uuid"],
                        chromosome=chromosome,
                        start=start,
                    )
                )
    sys.stdout.write("Writing out SQL queries for structural variants ...\n")
    with open("query_results_sv.tsv", "w") as fh:
        for query_uuid, query_result in query_results["svs"].items():
            for coords in query_result["orphans"]:
                chromosome, start_end = coords.split(":")
                start, end = start_end.split("-")
                fh.write(
                    SQL_QUERY_TEMPLATE.format(
                        db=SQL_SV_DB,
                        case_uuid=query_result["case_uuid"],
                        chromosome=chromosome,
                        start=start,
                    )
                )
    sys.stdout.write("Done with everything!\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: kickoff_orphaned_annotation_query.py <orphans.json>")
        sys.exit(1)
    main()
