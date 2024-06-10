.. _developer_data_builds:

====================
Docker & Data Builds
====================

This section describes how to build the Docker images and also the VarFish site data tarballs.
The intended audience are VarFish developers.

-------------------
Build Docker Images
-------------------

Building the image::

    $ ./docker/build-docker.sh

By default the latest tag is used.
You can change this with.

    $ GIT_TAG=v0.1.0 ./docker/build-docker.sh

------------------------------
Get ``varfish-docker-compose``
------------------------------

The database is built in ``varfish-docker-compose``.

::

    $ git clone git@github.com:varfish-org/varfish-docker-compose.git
    $ cd varfish-docker-compose
    $ ./init.sh

----------------------------
First-Time Container Startup
----------------------------

You have to startup the postgres container once to create the Postgres database.
Once it has been initialized, shutdown with Ctrl-C.

::

    $ docker-compose up postgres
    <Ctrl-C>

Now copy over the ``postgresql.conf`` file that has been tuned for the VarFish use cases.

::

    $ cp config/postgres/postgresql.conf volumes/postgres/data/postgresql.conf

Bring up the site again so we can build the database.

::

    $ docker-compose up

Wait until ``varfish-web`` is up and running and all migrations have been applied, look for ``VARFISH MIGRATIONS END`` in the output of ``run-docker-compose-up.sh``.

---------------------------
Pre-Build Postgres Database
---------------------------

Download static data

::

    $ cd /plenty/space
    $ wget https://file-public.bihealth.org/transient/varfish/anthenea/varfish-server-background-db-20201006.tar.gz{,.sha256}
    $ sha256sum -c varfish-server-background-db-20201006.tar.gz.sha256
    $ tar xzvf varfish-server-background-db-20201006.tar.gz

Adjust the ``docker-compose.yml`` file such that ``/plenty/space`` is visible in the varfish-web container.

::

    volumes:
        - "/plenty/space:/data"

Get the name of the running varfish-web container.

::

    $ docker ps
    CONTAINER ID   IMAGE                                                       COMMAND                  CREATED          STATUS              PORTS                                      NAMES
    44be6ece102e   minio/minio                                                 "/usr/bin/docker-ent…"   11 minutes ago   Up About a minute   9000/tcp                                   varfish-docker-compose_minio_1
    3b23113e5aa1   quay.io/biocontainers/exomiser-rest-prioritiser:12.1.0--1   "exomiser-rest-prior…"   11 minutes ago   Up About a minute                                              varfish-docker-compose_exomiser-rest-prioritiser_1
    b8c49e8c24a6   quay.io/biocontainers/jannovar-cli:0.33--0                  "jannovar -Xmx6G -Xm…"   11 minutes ago   Up About a minute                                              varfish-docker-compose_jannovar_1
    409a535b9951   varfish-org/varfish-server:0.22.1-0                            "docker-entrypoint.s…"   12 minutes ago   Up About a minute   8080/tcp                                   varfish-docker-compose_varfish-celerybeat_1
    7eb7425c59e2   varfish-org/varfish-server:0.22.1-0                            "docker-entrypoint.s…"   12 minutes ago   Up About a minute   8080/tcp                                   varfish-docker-compose_varfish-celeryd-import_1
    020811fde306   varfish-org/varfish-server:0.22.1-0                            "docker-entrypoint.s…"   12 minutes ago   Up About a minute   8080/tcp                                   varfish-docker-compose_varfish-celeryd-query_1
    87b03ee0249b   varfish-org/varfish-server:0.22.1-0                            "docker-entrypoint.s…"   12 minutes ago   Up About a minute   8080/tcp                                   varfish-docker-compose_varfish-celeryd-default_1
    7a3fdb337fae   varfish-org/varfish-server:0.22.1-0                            "docker-entrypoint.s…"   12 minutes ago   Up About a minute   8080/tcp                                   varfish-docker-compose_varfish-web_1
    9295a101570f   postgres:12                                                 "docker-entrypoint.s…"   12 minutes ago   Up About a minute   5432/tcp                                   varfish-docker-compose_postgres_1
    1c4d6e235074   traefik:v2.3.1                                              "/entrypoint.sh --pr…"   12 minutes ago   Up About a minute   0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp   varfish-docker-compose_traefik_1
    8d72fd096743   redis:6                                                     "docker-entrypoint.s…"   12 minutes ago   Up About a minute   6379/tcp                                   varfish-docker-compose_redis_1

Initialize the tables (while at least ``docker-compose up varfish-web postgres redis`` is running).

::

    $ docker exec -it -w /usr/src/app varfish-docker-compose_varfish-web_1 python manage.py import_tables --tables-path /data --threads 8

Then, shutdown the ``docker-compose up``, remove the ``volumes:`` entry for ``varfish-web``, and create a tarball of the postgres database to have a clean copy.

--------------
Add Other Data
--------------

Copy the other required data for ``jannovar`` and ``exomiser``.
You can find the appropriate files to download on the Jannovar (via Zenodo) and Exomiser data download sites:

- https://zenodo.org/record/5410367
- https://data.monarchinitiative.org/exomiser/data/index.html

You should use the hg19 data for Exomiser for any genome release as we will only use the the gene to phenotype prioritization that is independent of the genome release.

The result should look similar to this:

::

    # tree volumes/jannovar volumes/exomiser
    volumes/jannovar
    ├── hg19_ensembl.ser
    ├── hg19_refseq_curated.ser
    └── hg19_refseq.ser
    volumes/exomiser
    ├── 1909_hg19
    │   ├── 1909_hg19_clinvar_whitelist.tsv.gz
    .   .   [..]
    │   └── 1909_hg19_variants.mv.db
    └── 1909_phenotype
        ├── 1909_phenotype.h2.db
        ├── phenix
        │   ├── 10.out
        .   .   [..]
        │   ├── ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt
        │   ├── hp.obo
        │   └── phenotype_annotation.tab
        └── rw_string_10.mv

    3 directories, 55 files

------------------
Create a Superuser
------------------

While the ``docker-compose up`` is running

::

    $ docker exec -it -w /usr/src/app varfish-docker-compose_varfish-web_1 python manage.py createsuperuser
    Username: root
    Email address:
    Password: <changeme>
    Password (again): <changeme>
    Superuser created successfully.

------------------
Setup Initial Data
------------------

Create test category & project.

Obtain API key and configure ``varfish-cli``.

Import some test data through the API.

::

    $ varfish-cli --no-verify-ssl case create-import-info --resubmit \
        92f5d735-0967-4db2-a801-50fe96359f51 \
        $(find path/to/variant_export/work/*NA12878* -name '*.tsv.gz' -or -name '*.ped')


--------------------
Create Data Tarballs
--------------------

Now create the released data tarballs.

::

    tar -cf - volumes | pigz -c > varfish-site-data-v1-20210728-grch37.tar.gz && sha256sum varfish-site-data-v1-20210728-grch37.tar.gz >varfish-site-data-v1-20210728-grch37.tar.gz.sha256 &
    tar -cf - volumes | pigz -c > varfish-site-data-v1-20210728-grch38.tar.gz && sha256sum varfish-site-data-v1-20210728-grch38.tar.gz >varfish-site-data-v1-20210728-grch38.tar.gz.sha256 &
    tar -cf - test-data | pigz -c > varfish-test-data-v1-20211125.tar.gz && sha256sum varfish-test-data-v1-20211125.tar.gz >varfish-test-data-v1-20211125.tar.gz.sha256
