import json
import os
import sys
import time

import click
import requests
from rich.console import Console
import toml

#: Paths to search the global configuration in.
GLOBAL_CONFIG_PATHS = ("~/.varfishrc.toml",)

#: Endpoint to generate export tsv file
ENDPOINT_DOWNLOAD_GENERATE_TSV = "/variants/api/query-case/download/generate/tsv/{query_uuid}"
#: Endpoint to generate export vcf file
ENDPOINT_DOWNLOAD_GENERATE_VCF = "/variants/api/query-case/download/generate/vcf/{query_uuid}"
#: Endpoint to generate export xlsx file
ENDPOINT_DOWNLOAD_GENERATE_XLSX = "/variants/api/query-case/download/generate/xlsx/{query_uuid}"
#: Endpoint to download file
ENDPOINT_DOWNLOAD_SERVE = "/variants/api/query-case/download/serve/{sodar_uuid}"
#: Endpoint to check download status
ENDPOINT_DOWNLOAD_STATUS = "/variants/api/query-case/download/status/{sodar_uuid}"
#: Endpoint to case list
ENDPOINT_CASE_LIST = "/cases/api/case/list/{project_uuid}"
#: Endpoint to smallvariant query settings
ENDPOINT_SM_SETTINGS = "/variants/api/query-case/query-settings-shortcut/{case_uuid}"
#: Endpoint to smallvariant list-create query
ENDPOINT_SM_LISTCREATE_QUERY = "/variants/api/query/list-create/{case_uuid}"
#: Endpoint to smallvariant retrieve query
ENDPOINT_SM_RETRIEVE_QUERY = "/variants/api/query/retrieve-update-destroy/{query_uuid}/"
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


console = Console()


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


def run_query(
    config,
    settings_endpoint,
    query_endpoint,
    case_uuid,
    gene,
    region,
    quick_preset,
    inheritance,
    frequency,
    impact,
    verbose,
):
    url = settings_endpoint.format(case_uuid=case_uuid)
    url += f"?quick_preset={quick_preset}"
    if inheritance:
        url += f"&inheritance={inheritance}"
    if frequency:
        url += f"&frequency={frequency}"
    if impact:
        url += f"&impact={impact}"
    if verbose:
        console.log(url)
    response = connect_endpoint(config, url)
    if not response:
        return ""
    response_json = response.json()
    if gene:
        response_json["query_settings"]["gene_allowlist"] = [gene]
    elif region:
        response_json["query_settings"]["genomic_region"] = region
    url = query_endpoint.format(case_uuid=case_uuid)
    response = connect_endpoint(config, url, data=response_json)
    if not response:
        return ""
    response_json = response.json()
    if not response_json.get("sodar_uuid"):
        console.log(f"[bold red]Error: got no query uuid for case {case_uuid}[/bold red]")
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


def get_case_list(config, project_uuid):
    url = ENDPOINT_CASE_LIST.format(project_uuid=project_uuid)
    url_appendix = ""
    case_query = {}
    while True:
        response = connect_endpoint(config, url + ("?" + (url_appendix if url_appendix else "")))
        response_json = response.json()
        for case in response_json["results"]:
            case_query[case["sodar_uuid"]] = {"name": case["name"], "query": None}
        if not response_json["next"]:
            break
        url_appendix = response_json["next"].split("?")[1]
    return case_query


def download_generate(config, query_uuid, export_format):
    if export_format == "tsv":
        url = ENDPOINT_DOWNLOAD_GENERATE_TSV.format(query_uuid=query_uuid)
    elif export_format == "vcf":
        url = ENDPOINT_DOWNLOAD_GENERATE_VCF.format(query_uuid=query_uuid)
    elif export_format == "xlsx":
        url = ENDPOINT_DOWNLOAD_GENERATE_XLSX.format(query_uuid=query_uuid)
    response = connect_endpoint(config, url)
    if not response:
        return
    return response.json()["export_job__sodar_uuid"]


def download_status(config, sodar_uuid):
    url = ENDPOINT_DOWNLOAD_STATUS.format(sodar_uuid=sodar_uuid)
    response = connect_endpoint(config, url)
    if not response:
        return {}
    return response.json()["status"]


def download_serve(config, sodar_uuid, name):
    url = ENDPOINT_DOWNLOAD_SERVE.format(sodar_uuid=sodar_uuid)
    response = connect_endpoint(config, url)
    if not response:
        return
    with open(name, "wb") as fh:
        fh.write(response.content)


@click.command()
@click.argument("project-uuid")
@click.option(
    "--export-format",
    default="xlsx",
    type=click.Choice(["tsv", "vcf", "xlsx"], case_sensitive=False),
)
@click.option("--gene", default=None, help="Gene to filter on")
@click.option("--region", default=None, help="Region to filter on")
@click.option("--quick-preset", default="default", help="Quick preset to use")
@click.option("--inheritance", default=None, help="Inheritance preset to use")
@click.option("--frequency", default=None, help="Frequency preset to use")
@click.option("--impact", default=None, help="Impact preset to use")
@click.option("--verbose", is_flag=False, help="Verbose output")
def main(
    project_uuid, export_format, gene, region, quick_preset, inheritance, frequency, impact, verbose
):
    config = read_toml()
    query_results = {}
    case_query = {}

    with console.status("[bold green]Starting ..."):
        case_query = get_case_list(config, project_uuid)
        console.log("Getting cases from project [bold green]done[/bold green]")

    tasks = [
        f"Starting query for [bold]{case_query[n]['name']}[/bold] ({n})" for n in case_query.keys()
    ]
    with console.status("[bold green]Starting queries ..."):
        for case_uuid in case_query.keys():
            rich_query_start = tasks.pop(0)
            query_uuid = run_query(
                config,
                ENDPOINT_SM_SETTINGS,
                ENDPOINT_SM_LISTCREATE_QUERY,
                case_uuid,
                gene,
                region,
                quick_preset,
                inheritance,
                frequency,
                impact,
                verbose,
            )
            if not query_uuid:
                console.log(f"{rich_query_start} [bold red]failed[/bold red]")
                continue
            query_results[query_uuid] = {
                "running": True,
                "state": "initial",
                "case_uuid": case_uuid,
                "logs": [],
            }
            case_query[case_uuid]["query"] = query_uuid
            console.log(f"{rich_query_start} [bold green]done[/bold green]")

    with console.status("[bold green]Waiting for queries to finish ..."):
        while True:
            polls_running = poll_queries(config, ENDPOINT_SM_RETRIEVE_QUERY, query_results)
            if not polls_running:
                break
            time.sleep(SLEEP_POLL)

        if verbose:
            with open("query_logs.json", "w") as fh:
                json.dump(query_results, fh, indent=1)

    download_uuids = {}
    tasks = [
        f"Starting generation of export file for [bold]{case_query[query_results[n]['case_uuid']]['name']}[/bold] ({n})"
        for n in query_results.keys()
    ]
    with console.status("[bold green]Starting generation of export files ..."):
        for query_uuid, data in query_results.items():
            if data["state"] == "done":
                download_uuid = download_generate(config, query_uuid, export_format)
                if not download_uuid:
                    console.log(f"{tasks.pop(0)} [bold red]failed[/bold red]")
                    continue
                download_uuids[download_uuid] = case_query[data["case_uuid"]]["name"]
                console.log(f"{tasks.pop(0)} [bold green]done[/bold green]")
            else:
                console.log(f"{tasks.pop(0)} [bold red]failed[/bold red]")

    downloads_running = [True] * len(download_uuids)
    tasks = [f"Downloading file for [bold]{n}[/bold]" for n in download_uuids.values()]
    with console.status("[bold green]Waiting for downloads to finish ..."):
        while any(downloads_running):
            for i, download_uuid in enumerate(download_uuids):
                downloads_running[i] = download_status(config, download_uuid) == "running"
            time.sleep(SLEEP_POLL)

        for download_uuid, name in download_uuids.items():
            download_serve(config, download_uuid, f"{name}.{export_format}")
            console.log(f"{tasks.pop(0)} [bold green]done[/bold green]")
    console.log(":heavy_check_mark: [bold green]All done[/bold green]")


if __name__ == "__main__":
    main()
