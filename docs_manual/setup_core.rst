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

.. _setup_core_api:

-----------------
Setup VarFish API
-----------------

Setting up the API for use with VarFish can be done on any computer that should be able to use the VarFish API
(i.e. the computer you want to upload the data from). Most likely, this is not the VarFish Server itself but the
computer you have processed your data on.

Firstly, make sure that you have set up an API token as described in the section :ref:`ui_api_tokens`.
This enables you to easily import cases into VarFish.
Next, create a ``~/.varfishrc.toml`` file in your home directory on the computer that should be able to communicate
with the VarFish Server, and paste and adapt the following lines
(substitute ``VARFISH_IP``, ``VARFISH_PORT`` and ``VARFISH_API_TOKEN`` with your values):

.. code-block::

    [global]

    varfish_server_url = "http://VARFISH_IP:VARFISH_PORT/"
    varfish_api_token = "VARFISH_API_TOKEN"

Next, install the VarFish CLI on the computer that should be able to communicate with the VarFish Server.
For this, follow the instructions on PyPi for `VarFish CLI <https://pypi.org/project/varfish-cli/>`_.

.. _setup_core_varfish_annotator:

-----------------------
Setup VarFish Annotator
-----------------------

To prepare your files for upload to the VarFish Server, you have to install the VarFish Annotator on the
computer you want to process the data on (which is likely not the same computer you run the VarFish Server on).
The package is available in bioconda, and when you have set up a conda environment, you can easily install VarFish CLI:

.. code-block::

    conda install varfish-annotator-cli

Probably you want to have the VarFish Annotator and the VarFish CLI installed on the same computer.

.. _setup_core_varfish_database:

-----------------
Deploying VarFish
-----------------

Download the data packages from the public VarFish website and unpack it in a place that is large enough.

.. code-block:: bash

    cd /plenty/space/

    wget https://file-public.bihealth.org/transient/varfish/varfish-server-background-db-20201006.tar.gz{,.sha256}
    wget https://file-public.bihealth.org/transient/varfish/varfish-annotator-20201006.tar.gz{,.sha256}
    wget https://file-public.bihealth.org/transient/varfish/jannovar-db-20201006.tar.gz{,.sha256}

    sha256sum -c varfish-server-background-db-20201006.tar.gz.sha256
    sha256sum -c varfish-annotator-20201006.tar.gz.sha256
    sha256sum -c jannovar-db-20201006.tar.gz.sha256

    tar xzvf varfish-server-background-db-20201006.tar.gz
    tar xzvf varfish-annotator-20201006.tar.gz
    tar xzvf jannovar-db-20201006.tar.gz

Background Databases
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    varfish-manage import_tables --tables-path /plenty/space/varfish-server-background-db-20201006

.. note::

    The data import might take up to 24 hours.

Cases
^^^^^

On the computer you have the VarFish Annotator installed, the following commands will prepare your VCFs for upload to
the VarFish Server.

Annotate small variants of a case:

.. code-block:: bash

    varfish-annotator annotate \
        --case-id $CASE_NAME \
        --db-path /plenty/space/varfish-annotator-20201006/vvarfish-annotator-db-20201006.h2.db \
        --ensembl-ser-path /plenty/space/varfish-annotator-db-20201006/hg19_ensembl.ser \
        --input-vcf $INPUT_VCF \
        --output-db-info ${CASE_NAME}.db-info.gz \
        --output-gts ${CASE_NAME}.gts.tsv.gz \
        --refseq-ser-path /plenty/space/varfish-annotator-db-20201006/hg19_refseq_curated.ser \
        --release GRCh37

Annotate structural variants of a case:

.. code-block:: bash

    varfish-annotator annotate-svs \
        --case-id $CASE_NAME \
        --db-path /plenty/space/varfish-annotator-20201006/vvarfish-annotator-db-20201006.h2.db \
        --ensembl-ser-path /plenty/space/varfish-annotator-20201006/hg19_ensembl.ser \
        --input-vcf $INPUT_VCF \
        --output-db-info ${CASE_NAME}.db-info.gz \
        --output-feature-effects ${CASE_NAME}.effects.gts.tsv.gz \
        --output-gts ${CASE_NAME}.svs.gts.tsv.gz \
        --refseq-ser-path /plenty/space/varfish-annotator-20201006/hg19_refseq_curated.ser \
        --release GRCh37

After annotating and preparing the VCF files, you can use the VarFish CLI to import the data into the
VarFish Server via the API. Please also make md5 sum files available for each file:

.. code-block:: bash

    for i in ${CASE_NAME}.*; do md5sum $i > $i.md5; done

Import a small or structural variant case (replace the ``eee...eee`` UUID with your projects UUID):

.. code-block:: bash

    varfish-cli case create-import-info eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee ${CASE_NAME}.*

---------------------------
Create your own data freeze
---------------------------

In case you need different versions in the data import than provided, the VarFish DB Downloader allows you to do so.
Please follow the instructions in the `Varfish DB Downloader project <https://github.com/bihealth/varfish-db-downloader>`_.
