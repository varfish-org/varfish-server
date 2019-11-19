#!/bin/bash

set -x

# Make sure to unset database url when exiting the script.
function finish {
  unset DATABASE_URL
}
trap finish EXIT

# Set database url to varfish staging database
export DATABASE_URL="postgresql://varfish-staging:934RrGzsABOOVKuyRh8cdyGdz@cubi-postgres-kvm-2.bihealth.org/varfish-staging"
# Import gnomad exomes and genomes into varfish staging database
python manage.py import_tables --tables-path /cluster/fast/groups/cubi/work/scratch/varfish-db-downloader-finalizing-sv-dbs/ --force
