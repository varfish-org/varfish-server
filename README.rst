.. image:: https://readthedocs.org/projects/varfish-server/badge/?version=latest
    :target: https://varfish-server.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://app.codacy.com/project/badge/Grade/f47216cf5a4349acbb9baf5ca1c91329
    :target: https://www.codacy.com/gh/bihealth/varfish-server/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/varfish-server&amp;utm_campaign=Badge_Grade
.. image:: https://app.codacy.com/project/badge/Coverage/f47216cf5a4349acbb9baf5ca1c91329
    :target: https://www.codacy.com/gh/bihealth/varfish-server/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/varfish-server&amp;utm_campaign=Badge_Coverage
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

----------------------------------------
VarFish Data Release Compatibility Table
----------------------------------------

=====================  ============  ==============
VarFish DB Downloader  Data Release  VarFish Server
=====================  ============  ==============
v0.2                   20201006      <= v0.23
=====================  ============  ==============
