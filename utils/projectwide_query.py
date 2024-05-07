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

# TODO - The endpoints for structural variants are not yet used. They are placeholders for future development.

ENDPOINT_SV_SETTINGS = "/svs/ajax/query-case/query-settings-shortcut/{case_uuid}/?quick_preset=whole_genome&genotype_criteria=default&inheritance=any&frequency=any&impact=any&sv_type=any"
#: Endpoint to structuralvariant list-create query
ENDPOINT_SV_LISTCREATE_QUERY = "/svs/ajax/sv-query/list-create/{case_uuid}/"
#: Endpoint to structuralvariant retrieve query
ENDPOINT_SV_RETRIEVE_QUERY = "/svs/ajax/sv-query/retrieve-update-destroy/{query_uuid}/"

#: Sleep time between starting queries
SLEEP_RUN_DEFAULT = 5
#: Sleep time between polling queries
SLEEP_POLL = 5


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
    genes,
    region,
    quick_preset,
    inheritance,
    frequency,
    quality,
    impact,
):
    url = settings_endpoint.format(case_uuid=case_uuid)
    url += f"?quick_preset={quick_preset}"
    if inheritance:
        url += f"&inheritance={inheritance}"
    if frequency:
        url += f"&frequency={frequency}"
    if impact:
        url += f"&impact={impact}"
    if quality:
        url += f"&quality={quality}"
    response = connect_endpoint(config, url)
    if not response:
        return ""
    query_settings = response.json()
    if genes:
        query_settings["query_settings"]["gene_allowlist"] = genes.split(",")
    elif region:
        query_settings["query_settings"]["genomic_region"] = region
    url = query_endpoint.format(case_uuid=case_uuid)
    response = connect_endpoint(config, url, data=query_settings)
    if not response:
        return ""
    response_json = response.json()
    return response_json.get("sodar_uuid"), query_settings


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
@click.option("--genes", default=None, help="Genes to filter on, separated by ,")
@click.option("--region", default=None, help="Region to filter on")
@click.option("--quick-preset", default="defaults", help="Quick preset to use")
@click.option("--inheritance", default=None, help="Inheritance preset to use")
@click.option("--frequency", default=None, help="Frequency preset to use")
@click.option("--quality", default=None, help="Quality preset to use")
@click.option("--impact", default=None, help="Impact preset to use")
@click.option("--run-wait-secs", default=SLEEP_RUN_DEFAULT, help="Seconds to wait between runs")
@click.option("--write-query-logs", is_flag=True, help="Write query logs to file")
@click.option(
    "--write-query-settings", is_flag=True, help="Write query settings for each case to file"
)
def main(
    project_uuid,
    export_format,
    genes,
    region,
    quick_preset,
    inheritance,
    frequency,
    quality,
    impact,
    run_wait_secs,
    write_query_logs,
    write_query_settings,
):
    config = read_toml()
    query_results = {}
    case_query = {}
    path = project_uuid

    with console.status("[bold green]Starting ..."):
        case_query = get_case_list(config, project_uuid)
        console.log(f"Getting {len(case_query)} cases from project [bold green]done[/bold green]")

    if os.path.exists(path):
        console.log(f"[bold red]path `{path}` already exists[/bold red]")
        return

    os.mkdir(path)
    console.log(f"Created directory {path} [bold green]done[/bold green]")

    tasks = [
        f"{i+1}/{len(case_query)} Starting query for [bold]{case_query[n]['name']}[/bold] ({n})"
        for i, n in enumerate(case_query.keys())
    ]
    with console.status("[bold green]Starting queries ..."):
        for case_uuid in case_query.keys():
            rich_query_start = tasks.pop(0)
            case_name = case_query[case_uuid]["name"]
            query_uuid, query_settings = run_query(
                config,
                ENDPOINT_SM_SETTINGS,
                ENDPOINT_SM_LISTCREATE_QUERY,
                case_uuid,
                genes,
                region,
                quick_preset,
                inheritance,
                frequency,
                quality,
                impact,
            )
            if write_query_settings and query_settings:
                with open(f"{path}/{case_name}.json", "w") as fh:
                    json.dump(query_settings, fh, indent=1)
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
            time.sleep(run_wait_secs)

    with console.status("[bold green]Waiting for queries to finish ..."):
        while True:
            polls_running = poll_queries(config, ENDPOINT_SM_RETRIEVE_QUERY, query_results)
            if not polls_running:
                break
            time.sleep(SLEEP_POLL)

        if write_query_logs:
            with open(f"{path}/query_logs.json", "w") as fh:
                json.dump(query_results, fh, indent=1)

    download_uuids = {}
    total_queries = len(query_results)
    tasks = [
        f"{i+1}/{total_queries} Starting generation of export file for [bold]{case_query[query_results[n]['case_uuid']]['name']}[/bold] ({n})"
        for i, n in enumerate(query_results.keys())
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
    tasks = [
        f"{i+1}/{len(download_uuids)} Downloading file for [bold]{n}[/bold]"
        for i, n in enumerate(download_uuids.values())
    ]
    with console.status("[bold green]Waiting for downloads to finish ..."):
        while any(downloads_running):
            for i, download_uuid in enumerate(download_uuids):
                downloads_running[i] = download_status(config, download_uuid) == "running"
            time.sleep(SLEEP_POLL)

        for download_uuid, name in download_uuids.items():
            download_serve(config, download_uuid, f"{path}/{name}.{export_format}")
            console.log(f"{tasks.pop(0)} [bold green]done[/bold green]")
    console.log(":heavy_check_mark: [bold green]All done[/bold green]")


if __name__ == "__main__":
    main()
