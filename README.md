[![Documentation Status](https://readthedocs.org/projects/varfish-server/badge/?version=latest)](https://varfish-server.readthedocs.io/en/latest/?badge=latest)
[![Code Coverage](https://codecov.io/gh/varfish-org/varfish-server/branch/main/graph/badge.svg?token=5ZACSH5MZZ)](https://codecov.io/gh/varfish-org/varfish-server)
[![image](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

# VarFish

**Comprehensive DNA variant analysis for diagnostics and research.**

This is the repository for the web server component.

Holtgrewe, M.; Stolpe, O.; Nieminen, M.; Mundlos, S.; Knaus, A.; Kornak, U.; Seelow, D.; Segebrecht, L.; Spielmann, M.; Fischer-Zirnsak, B.; Boschann, F.; Scholl, U.; Ehmke, N.; Beule, D. *VarFish: Comprehensive DNA Variant Analysis for Diagnostics and Research*. Nucleic Acids Research 2020, gkaa241. <https://doi.org/10.1093/nar/gkaa241>.

## Getting Started

- [VarFish Homepage](https://www.cubi.bihealth.org/software/varfish/)
- [Manual](https://varfish-server.readthedocs.io/en/latest/)
  - [Installation Instructions](https://varfish-server.readthedocs.io/en/latest/admin_install.html).
- [Docker Compose Installer](https://github.com/varfish-org/varfish-docker-compose#run-varfish-server-using-docker-compose).

## VarFish Repositories

- [varfish-server](https://github.com/varfish-org/varfish-server) The VarFish Server is the web frontend used by the end users / data analysts.
- [varfish-annotator](https://github.com/varfish-org/varfish-annotator) The VarFish Annotator is a command line utility used for annotating VCF files and converting them to files that can be imported into VarFish Server.
- [varfish-cli](https://github.com/varfish-org/varfish-cli) The VarFish Command Line Interface allows to import data through the VarFish REST API.
- [varfish-db-downloader](https://github.com/varfish-org/varfish-db-downloader) The VarFish DB Downloader is a command line tool for downloading the background database.
- [varfish-docker-compose](https://github.com/varfish-org/varfish-docker-compose) Quickly get started running a VarFish server by using Docker Compose. We provide a prebuilt data set with some already imported data.

## At a Glance

- License: MIT
- Dependencies / Tech Stack
  - Python \>=3.8
  - Django 3
  - PostgreSQL \>=12

GitHub is used for public issue tracking. Currently, development happens
on internal infrastructure.

## VarFish Component Compatibility Table

The following combinations have been validated / are supported to work.

| VarFish Server | VarFish CLI | VarFish Annotator |
| -------------- | ----------- | ----------------- |
| v1.2.2         | v0.3.0      | v0.21             |
| v1.2.1         | v0.3.0      | v0.21             |
| v1.2.0         | v0.3.0      | v0.21             |

## VarFish Data Release Compatibility Table

The following combinations have been validated / are supported to work.

| VarFish Server | Data Release | VarFish DB Downloader |
| -------------- | ------------ | --------------------- |
| v1.2.2         | 20210728c    | v0.3.\*               |
| v1.2.1         | 20210728     | v0.3.\*               |
| v1.2.1         | 20210728b    | v0.3.\*               |
| v1.2.0         | 20210728     | v0.3.\*               |
| v1.2.0         | 20210728b    | v0.3.\*               |
