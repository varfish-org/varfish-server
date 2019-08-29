.. _setup_core:

==================================
Installing VarFish Core Components
==================================

This chapter describes how to install the VarFish core components and their requirements.
The audience of this chapter are those who want to install VarFish on their own infrastructure.

.. note::

    For setting up VarFish, some knowledge of Linux administration skills will be necessary.
    If you fulfill all prerequisites and follow the guide below, the installation should go smoothly and not too much knowledge will be required.
    In case of problems, Linux administration skills will come in handy, though.

    In case of any problems, please open an issue in the `Github project issue tracker <https://github.com/bihealth/varfish-server/issues>`_.

.. _setup_core_prerequisites:

------------
Requirements
------------

Generally, VarFish can be installed as a normal user on a Linux workstation (or even macOS or Windows).
For the sake of simplicity, however, the instructions below describe the streamlined deployment to Linux systems and your mileage might vary if you are straying from this.

A VarFish installation consists of a Python-based Django application and a PostgreSQL database (*web app server*).
The main work is done in the PostgreSQL database (*database server*).

For the **web app server**, we assume that you have a Linux server with root access dedicated to running VarFish.
As most work is done on the database server, a moderst (virtual) machine will work nicely.
The VarFish requirements are:

- Supported Operating Systems:
  - CentOS 7
  - Ubuntu 16.04 and 18.04
- 1 GB of free disk space
- 4 cores (better: 8+ cores)
- 16 GB of RAM (better: 32+ GB)

For the **database server**, the requirements are:

- PostgreSQL 11 installation (or any later version).
  Our Ansible playbooks can install one for you on CentOS 7 or Ubuntu Linux 16.04/18.04.
- 100 GB of free disk space (if you have many exomes, we recommend 1+ TB)
- 2 cores (better: 4+ cores)
- 32 GB of RAM (better: 64+ GB)
- as fast disks as you can get

Tuning database servers is an art of its own and you can have a look at the section :ref:`setup_tuning` for getting started.

.. _setup_core_preparation:

-----------
Preparation
-----------

We describe the installation of VarFish using `Ansible <https://www.ansible.com/>`_, an IT automatisation tool.
If you want to use another deployment tool or install it by hand, you will need to infer the different steps from the Ansible scripts (known as playbooks and roles).
We show the example code for Ubuntu 16.04/18.04 and CentOS 7 (we're happy to accept contributions for other OS).

First, install Ansible itself:

.. code-block:: bash

    ## Ubuntu

    sudo add-apt-repository ppa:ansible/ansible
    sudo apt-get update
    sudo apt-get install -y ansible

    ## CentOS

    sudo yum install -y epel-release
    sudo yum install -y ansible

Next, install the dependencies for the Ansible playbooks and roles that we will use:

.. code-block:: bash

    export PATH=$HOME/.local/bin:$PATH
    echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
    pip install --user -U pip
    pip install --user dnspython

Finally, setup an Ansible project directory:

.. code-block:: bash

    mkdir -p varfish-ansible
    cd varfish-ansible

    cat >inventory <<EOF
    [varfish_servers]
    # Use the following if your server has a real DNS entry.
    varfish-server.example.com
    # Alternatively, use the following if you only have an IP.
    # varfish-server ansible_host=127.0.0.1  # <-- the IP here

    # If you want to install and manage your Postgres server with Ansible, define the following.
    # [postgres_servers]
    # postgres-server.example.com
    ## OR
    # postgres-server ansible_host=127.0.0.1  # <-- the IP here
    EOF

    cat >varfish.yml <<EOF
    ---

    - name: install varfish
      hosts: varfish_servers
      roles:
        - role: bihealth.ssh_keys
          tags: ssh
        - role: bihealth.basic_server
          tags: basics
        - role: bihealth.varfish_server
          tags: varfish
      vars:
        # bihealth.sodar_core_app ---------------------------------------------------------------------
        sodar_core_app_version: "master"
        sodar_core_app_django_secret_key: "SECRETSECRETSECRETSECRETSECRETSECRET"
        sodar_core_app_superuser_password: "changeme123"
        # bihealth.postgres_client --------------------------------------------------------------------
        # Uncomment the following line if you want to manage the Postgres server with Ansible.
        # postgres_client_create_user_and_db: true
        postgres_client_host: postgres-server.example.com
        # If you want to manage your Postgres server with Ansible, configure the desired user and
        # database name as well as the password here.  If you have your Postgres datbase setup
        # independently, adjust to the database and user name and the password here.
        postgres_client_db: "varfish-test"
        postgres_client_user: "varfish-test"
        postgres_client_password: "secret-password"
        # bihealth.ssh_keys ---------------------------------------------------------------------------
        ssh_keys_user_keys:
          - user: root
        # bihealth.ssl_certs --------------------------------------------------------------------------
        # If you do not specify cert/key then this will create a self-signed certificate for the
        # server.  Otherwise, you can put the certificate here.
        ssl_certs_certs:
          - name: "{{ inventory_hostname }}"
        #     cert: |
        #       -----BEGIN CERTIFICATE-----
        #       [...]
        #       -----END CERTIFICATE-----
        #     key: |
        #       -----BEGIN RSA PRIVATE KEY-----
        #       [...]
        #       -----END RSA PRIVATE KEY-----
    EOF

    # Optional, only if you want to manage your Postgres server with Ansible.
    cat >postgres.yml <<EOF
    TODO
    EOF

.. note::

    Of course, putting clear text passwords and SSL private keys into configuration is not security best practice.
    Ansible provides a number of features for keeping such secrets encrypted but that is beyond the scope of this manual.
    We recommend having a look into the `passwordstore Ansible plugin <https://docs.ansible.com/ansible/latest/plugins/lookup/passwordstore.html>`_.

.. _setup_core_postgresql_database:

----------------------------
Creating PostgreSQL Database
----------------------------

Create an empty postgres database named ``varfish``:

.. code-block:: bash

    sudo su postgres
    createdb varfish
    exit

Let VarFish create the required tables in the ``varfish`` database:

.. code-block:: bash

    varfish-manage migrate

.. _setup_core_varfish_database:

-----------------
Deploying VarFish
-----------------

Download the data packages from the public VarFish website and unpack it in a place that is large enough.

.. code-block:: bash

    cd /plenty/space/
    wget https://file-public.bihealth.org/transient/varfish/varfish-server-background-db-20190820.tar.gz
    wget https://file-public.bihealth.org/transient/varfish/varfish-annotator-transcripts-2019020.tar.gz
    wget https://file-public.bihealth.org/transient/varfish/varfish-annotator-db-20190820.h2.db.gz
    tar xzvf varfish-server-background-db-20190820.tar.gz
    tar xvvf varfish-annotator-transcripts-20190820.tar.gz
    gunzip varfish-annotator-db-20190820.h2.db.gz

Background Databases
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    varfish-manage import_tables --tables-path /plenty/space/varfish-server-background-db-20190820

.. note::

    The data import might take up to 24 hours.

Cases
^^^^^

Annotate small variants of a case:

.. code-block:: bash

    varfish-annotator annotate \
        --case-id $CASE_NAME \
        --db-path /plenty/space/varfish-annotator-db-20190820.h2.db \
        --ensembl-ser-path /plenty/space/varfish-annotator-transcripts-20190820/hg19_ensembl.ser \
        --input-vcf $INPUT_VCF \
        --output-db-info ${CASE_NAME}.db-info.gz \
        --output-gts ${CASE_NAME}.gts.tsv.gz \
        --refseq-ser-path /plenty/space/varfish-annotator-transcripts-20190820/hg19_refseq_curated.ser \
        --release GRCh37

Annotate structural variants of a case:

.. code-block:: bash

    varfish-annotator annotate-svs \
        --case-id $CASE_NAME \
        --db-path /plenty/space/varfish-annotator-db-20190820.h2.db \
        --ensembl-ser-path /plenty/space/varfish-annotator-transcripts-20190820/hg19_ensembl.ser \
        --input-vcf $INPUT_VCF \
        --output-db-info ${CASE_NAME}.db-info.gz \
        --output-feature-effects ${CASE_NAME}.effects.gts.tsv.gz \
        --output-gts ${CASE_NAME}.svs.gts.tsv.gz \
        --refseq-ser-path /plenty/space/varfish-annotator-transcripts-20190820/hg19_refseq_curated.ser \
        --release GRCh37

Import a small variant case (replace UUID with your projects UUID):

.. code-block:: bash

    varfish-manage import_case \
        --case-name $CASE_NAME \
        --index-name $INDEX_NAME \
        --path-ped $PATH_PED \
        --path-genotypes ${CASE_NAME}.gts.tsv.gz \
        --path-db-info ${CASE_NAME}.db-info.gz \
        --project-uuid eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee

Import a structural variant case (replace UUID with your projects UUID):

.. code-block:: bash

    varfish-manage import_case \
        --case-name $CASE_NAME \
        --index-name $INDEX_NAME \
        --path-ped $PATH_PED \
        --path-genotypes ${CASE_NAME}.svs.gts.tsv.gz \
        --path-feature-effects {$CASE_NAME}.effects.gts.tsv.gz \
        --path-db-info ${CASE_NAME}.db-info.gz \
        --project-uuid eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee

---------------------------
Create your own data freeze
---------------------------

In case you need different versions in the data import than provided, the VarFish DB Downloader allows you to do so.
First, clone the repository:

.. code-block:: bash

    git clone git@cubi-gitlab.bihealth.org:CUBI_Engineering/VarFish/varfish-db-downloader
    cd varfish-db-downloader

Create a conda environment that provides all necessary programs tob run the data import.

.. code-block:: bash

    conda env create -n varfish-db-downloader -f environment.yaml
    conda activate varfish-db-downloader
    pip install -r requirements.txt

Running the actual is done with one command. You might want to adapt versions to your need in the source code,
especially in the ``Snakefile`` and ``snakefiles/*``.

.. code-block:: bash

    snakemake

.. note::

    This might take some time, depending on your internet connection.
    Make also sure that you provide at least 1.5 TB of space.
    Also, note that this heavily relies on external data providers and therefore might contain broken links.
    In case you encounter them, please open an issue in the `Github project issue tracker <https://github.com/bihealth/varfish-server/issues>`_.

.. code-block:: bash

    conda create -n varfish-annotator varfish-annotator-cli jannovar-cli
    conda activate varfish-annotator

Adapt ``ANNOTATOR_DATA_RELEASE`` and ``ANNOTATOR_VERSION`` to the current values in the following
code snippet.

.. code-block:: bash

    ANNOTATOR_DATA_RELEASE=20190820
    ANNOTATOR_VERSION=0.9
    DOWNLOAD=varfish-db-downloader-finalizing-sv-dbs/varfish-annotator-db-$ANNOTATOR_DATA_RELEASE/

.. code-block:: bash

    tar chzvf \
        varfish-annotator-db-$ANNOTATOR_DATA_RELEASE.tar.gz \
        varfish-annotator-db-$ANNOTATOR_DATA_RELEASE/
    sha256sum \
        varfish-annotator-db-$ANNOTATOR_DATA_RELEASE.tar.gz \
        > varfish-annotator-db-$ANNOTATOR_DATA_RELEASE.tar.gz.sha256

.. code-block:: bash

    jannovar download \
        -d hg19/refseq_curated \
        --download-dir varfish-annotator-transcripts-$ANNOTATOR_DATA_RELEASE
    jannovar download \
        -d hg19/ensembl \
        --download-dir varfish-annotator-transcripts-$ANNOTATOR_DATA_RELEASE
    tar czvf \
        varfish-annotator-transcripts-$ANNOTATOR_DATA_RELEASE.tar.gz \
        varfish-annotator-transcripts-$ANNOTATOR_DATA_RELEASE/*.ser
    sha256sum \
        varfish-annotator-transcripts-$ANNOTATOR_DATA_RELEASE.tar.gz \
        > varfish-annotator-transcripts-$ANNOTATOR_DATA_RELEASE.tar.gz.sha256

.. code-block:: bash

    varfish-annotator init-db \
        --db-release-info "varfish-annotator:v$ANNOTATOR_VERSION" \
        --db-release-info "varfish-annotator-db:r$ANNOTATOR_DATA_RELEASE" \
        \
        --ref-path $DOWNLOAD/GRCh37/reference/hs37d5/hs37d5.fa \
        \
        --db-release-info "clinvar:2019-06-22" \
        --clinvar-path $DOWNLOAD/GRCh37/clinvar/latest/clinvar_tsv_main/output/clinvar_allele_trait_pairs.single.b37.tsv.gz \
        --clinvar-path $DOWNLOAD/GRCh37/clinvar/latest/clinvar_tsv_main/output/clinvar_allele_trait_pairs.multi.b37.tsv.gz \
        \
        --db-path ./varfish-annotator-db-$ANNOTATOR_DATA_RELEASE \
        \
        --db-release-info "exac:r1.0" \
        --exac-path $DOWNLOAD/GRCh37/ExAC/r1/download/ExAC.r1.sites.vep.vcf.gz \
        \
        --db-release-info "gnomad_exomes:r2.1" \
        $(for path in $DOWNLOAD/GRCh37/gnomAD_exomes/r2.1/download/gnomad.exomes.r2.1.sites.chr*.normalized.vcf.bgz; do \
            echo --gnomad-exomes-path $path; \
        done) \
        \
        --db-release-info "gnomad_genomes:r2.1" \
        $(for path in $DOWNLOAD/GRCh37/gnomAD_genomes/r2.1/download/gnomad.genomes.r2.1.sites.chr*.normalized.vcf.bgz; do \
            echo --gnomad-genomes-path $path; \
        done) \
        \
        --db-release-info "thousand_genomes:v3.20101123" \
        --thousand-genomes-path $DOWNLOAD/GRCh37/thousand_genomes/phase3/ALL.phase3_shapeit2_mvncall_integrated_v5a.20130502.sites.vcf.gz \
        \
        --db-release-info "hgmd_public:ensembl_r75" \
        --hgmd-public $DOWNLOAD/GRCh37/hgmd_public/ensembl_r75/HgmdPublicLocus.tsv
    gzip -c \
        varfish-annotator-db-${ANNOTATOR_DATA_RELEASE}.db.h2 \
        > varfish-annotator-db-${ANNOTATOR_DATA_RELEASE}.db.h2.gz
    sha256sum \
        varfish-annotator-db-${ANNOTATOR_DATA_RELEASE}.h2.db.gz \
        > varfish-annotator-db-${ANNOTATOR_DATA_RELEASE}.h2.db.gz.sha256
