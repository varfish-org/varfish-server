.. image:: https://readthedocs.org/projects/varfish-server/badge/?version=latest
    :target: https://varfish-server.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://coveralls.io/repos/github/bihealth/varfish-server/badge.svg?branch=main
    :target: https://coveralls.io/github/bihealth/varfish-server?branch=main
.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :target: https://opensource.org/licenses/MIT


=======
VarFish
=======

**Comprehensive DNA variant analysis for diagnostics and research.**

This is the repository for the web server component.


Holtgrewe, M.; Stolpe, O.; Nieminen, M.; Mundlos, S.; Knaus, A.; Kornak, U.; Seelow, D.; Segebrecht, L.; Spielmann, M.; Fischer-Zirnsak, B.; Boschann, F.; Scholl, U.; Ehmke, N.; Beule, D.
*VarFish: Comprehensive DNA Variant Analysis for Diagnostics and Research*.
Nucleic Acids Research 2020, gkaa241.
https://doi.org/10.1093/nar/gkaa241.

---------------
Getting Started
---------------

- `VarFish Homepage <https://www.cubi.bihealth.org/software/varfish/>`__
- `Manual <https://varfish-server.readthedocs.io/en/latest/>`__
    - `Installation Instructions <https://varfish-server.readthedocs.io/en/latest/admin_install.html>`__.
- `Docker Compose Installer <https://github.com/bihealth/varfish-docker-compose#run-varfish-server-using-docker-compose>`__.

--------------------
VarFish Repositories
--------------------

`varfish-server <https://github.com/bihealth/varfish-server>`__
    The VarFish Server is the web frontend used by the end users / data analysts.
`varfish-annotator <https://github.com/bihealth/varfish-annotator>`__
    The VarFish Annotator is a command line utility used for annotating VCF files and converting them to files that can be imported into VarFish Server.
`varfish-cli <https://github.com/bihealth/varfish-cli>`__
    The VarFish Command Line Interface allows to import data through the VarFish REST API.
`varfish-db-downloader <https://github.com/bihealth/varfish-db-downloader>`__
    The VarFish DB Downloader is a command line tool for downloading the background database.
`varfish-docker-compose <https://github.com/bihealth/varfish-docker-compose>`__
    Quickly get started running a VarFish server by using Docker Compose.
    We provide a prebuilt data set with some already imported data.

-----------
At a Glance
-----------

- License: MIT
- Dependencies / Tech Stack
    - Python >=3.7
    - Django 3
    - PostgreSQL >=12

GitHub is used for public issue tracking.
Currently, development happens on internal infrastructure.

-------------------------------------
VarFish Component Compatibility Table
-------------------------------------

The following combinations have been validated / are supported to work.

==============  ===========  =================
VarFish Server  VarFish CLI  VarFish Annotator
==============  ===========  =================
v1.2.2          v0.3.0       v0.21
v1.2.1          v0.3.0       v0.21
v1.2.0          v0.3.0       v0.21
==============  ===========  =================

----------------------------------------
VarFish Data Release Compatibility Table
----------------------------------------

The following combinations have been validated / are supported to work.

==============  ============  =====================
VarFish Server  Data Release  VarFish DB Downloader
==============  ============  =====================
v1.2.2          20210728c     v0.3.*
v1.2.1          20210728      v0.3.*
v1.2.1          20210728b     v0.3.*
v1.2.0          20210728      v0.3.*
v1.2.0          20210728b     v0.3.*
==============  ============  =====================
