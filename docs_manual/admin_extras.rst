.. _admin_extras:

==============
Extra Services
==============

This section describes the installation of extra services.

.. _admin_extras_cadd_scripts:

-------------------------
Install Scoring with CADD
-------------------------

This section describes how to enable the scoring of variants with CADD using the `CADD-scripts <https://github.com/kircherlab/CADD-scripts>`__ provided by the CADD authors.
Note well that CADD-scripts is only free for non-commercial users as expressed in the `CADD-scripts license <https://github.com/kircherlab/CADD-scripts/blob/master/LICENSE>`__.
The installation is described for using a VarFish Docker Compose based installation.

First, create a directory ``volumes/cadd-rest-api`` inside the ``varfish-docker-compose`` directory and download an updated version of the install script.

.. code-block:: console

    $ cd varfish-docker-compose
    $ mkdir -p volumes/cadd-rest-api/db
    $ curl https://raw.githubusercontent.com/kircherlab/CADD-scripts/7502f47/install.sh \
        > volumes/cadd-rest-api/install.sh

Next, download the appropriate files using the ``install.sh`` script you just downloaded.
The script will ask you for some decisions and the corresponding lines are highlighted below.

.. code-block:: console
    :emphasize-lines: 13-20

    $ docker run -it -e CADD=/opt/miniconda3/share/cadd-scripts-1.6-0 \
        -v $PWD/volumes/cadd-rest-api:/data bihealth/cadd-rest-api:0.3.1-0 \
        bash /data/install.sh -b
    Using kircherlab.bihealth.org as download server
    CADD-v1.6 (c) University of Washington, Hudson-Alpha Institute for Biotechnology and Berlin Institute of Health 2013-
    2020. All rights reserved.

    The following questions will quide you through selecting the files and dependencies needed for CADD.
    After this, you will see an overview of the selected files before the download and installation starts.
    Please note, that for successfully running CADD locally, you will need the conda environment and at least one set of
    annotations.

    Do you want to install the virtual environments with all CADD dependencies via conda? (y)/n n
    Do you want to install CADD v1.6 for GRCh37/hg19? (y)/n y
    Do you want to install CADD v1.6 for GRCh38/hg38? (y)/n n
    Do you want to load annotations (Annotations can also be downloaded manually from the website)? (y)/n y
    Do you want to load prescored variants (Makes SNV calling faster. Can also be loaded/installed later.)? y/(n) y
    Do you want to load prescored variants for scoring with annotations (Warning: These files are very big)? y/(n) y
    Do you want to load prescored variants for scoring without annotations? y/(n) y
    Do you also want to load prescored InDels? We provide scores for well known InDels from sources like ClinVar, gnomAD/TOPMed etc. y/(n) y

    The following will be loaded: (disk space occupied)
     - Download CADD annotations for GRCh37-v1.6 (121 GB)
     - Download prescored SNV inclusive annotations for GRCh37-v1.6 (248 GB)
     - Download prescored InDels inclusive annotations for GRCh37-v1.6 (3.4 GB)
     - Download prescored SNV (without annotations) for GRCh37-v1.6 (78 GB)
     - Download prescored InDels (without annotations) for GRCh37-v1.6 (0.6 GB)
    Please make sure you have enough disk space available.
    Ready to continue? (y)/n y
    Starting installation. This will take some time.
    [...]
    Connecting to kircherlab.bihealth.org (kircherlab.bihealth.org)|141.80.169.4|:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 61 [application/x-gzip]
    Saving to: ‘InDels_inclAnno.tsv.gz.tbi.md5’

    InDels_inclAnno.tsv.gz.tbi.md5             100%[======================================================================================>]      61  --.-KB/s    in 0s
    2021-03-08 18:55:10 (19.9 MB/s) - ‘InDels_inclAnno.tsv.gz.tbi.md5’ saved [61/61]

    InDels_inclAnno.tsv.gz: OK
    InDels_inclAnno.tsv.gz.tbi: OK

Then, update the ``.env`` file by uncommenting the lines that configure the variant prioritization with CADD in VarFish (use the contents of the ``.env`` file as the lines below might not be completely up to date).

.. code-block:: bash

    # Extra: CADD REST API *****************************************************

    # Uncomment the following lines to enable variant prioritization using the
    # CADD score.  See the VarFish Server manual for installation instructions,
    # in particular how to download the required data.
    VARFISH_ENABLE_CADD=1
    VARFISH_CADD_REST_API_URL=http://cadd-rest-api:8080
    VARFISH_CADD_MAX_VARS=5000

Also, uncomment the lines in the ``docker-compose.yml`` file for the ``cadd-rest-api-server`` and ``cadd-rest-api-celeryd`` containers (the following listing is redacted, the ``docker-compose.yml`` file is up to date).

.. code-block:: yaml

    # Uncomment the following lines to enable the CADD REST API server that
    # is used for variant prioritization using the CADD score.  We need both
    # the server and the CADD-based worker.
    cadd-rest-api-server:
      image: bihealth/cadd-rest-api:0.3.1-0
      env_file: cadd-rest-api.env
      command: ["wsgi"]
      # [...]

    # You have to provide multiple cadd-rest-api-celeryd-worker container if
    # you want to handle more than one query at a time.
    cadd-rest-api-celeryd-worker-1:
    [...]
    cadd-rest-api-celeryd-worker-3:
      image: bihealth/cadd-rest-api:0.3.2-0
      env_file: cadd-rest-api.env
      command: ["celeryd"]
      networks: [varfish]
      restart: unless-stopped
      volumes:
        - "./volumes/cadd-rest-api/data/annotations:/opt/miniconda3/share/cadd-scripts-1.6-0/data/annotations:ro"
        - "./volumes/cadd-rest-api/data/prescored:/opt/miniconda3/share/cadd-scripts-1.6-0/data/prescored:ro"
        - "./volumes/cadd-rest-api/db:/data/db:rw"

Finally, restart your Docker container cluster including the new containers with ``docker-compose down && docker-compose up -d``.
