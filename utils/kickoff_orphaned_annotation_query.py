import json
import sys

import requests

BASE_URL = "http://"
TOKEN = "XXX"
SETTINGS_URL = f"{BASE_URL}/variants/api/query-case/query-settings-shortcut"
QUERY_URL = f"{BASE_URL}/variants/api/query/list-create"


headers = {"Authorization": "TOKEN " + TOKEN}


def read_file(file):
    with open(file, "r") as f:
        return json.load(f)


def main():
    orphans = read_file(sys.argv[1])
    for case_uuid, case_orphans in orphans.items():
        if not case_orphans["small_variants"]:
            continue
        response = requests.get(f"{SETTINGS_URL}/{case_uuid}/", headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.status_code} ({case_uuid})")
            continue
        response = response.json()
        response["query_settings"]["selected_variants"] = case_orphans["small_variants"]
        response = requests.post(f"{QUERY_URL}/{case_uuid}/", headers=headers, json=response)
        print(
            f"Query created for case {case_uuid}, {len(case_orphans['small_variants'])} orphans, status code: {response.status_code}"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: kickoff_orphaned_annotation_query.py <orphans.json>")
        sys.exit(1)
    main()
