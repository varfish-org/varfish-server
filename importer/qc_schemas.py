"""Utility code for QC schemas."""

import os.path
import json


def load_json(path):
    """Helper function to load JSON file relative to project root directory."""
    full_path = os.path.join(os.path.dirname(__file__), "..", path)
    with open(full_path, "rt") as inputf:
        return json.load(inputf)


#: QC schema v1
SCHEMA_QC_V1 = load_json("importer/schemas/case-qc-v1.json")
