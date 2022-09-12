.. _admin_upgrade:

============================
Upgrade Varfish Installation
============================

This section contains upgrade instructions for upgrading your VarFish Server installation using `VarFish Docker Compose <https://github.com/bihealth/varfish-docker-compose>`__.

.. _admin_upgrade_data_release_20210728:

-------------------------------------------------
Problem with Data Release ``20210728`` and GRCh37
-------------------------------------------------

The data release has a problem with the GRCh37 extra annotations.
If you can then use the updated site data ``20210728b`` release.
If you already have an instance with ``20210728`` background data then you can use the following data file.

- `varfish-server-background-db-20210728-grch37-patch-20210728b.tar.gz <https://file-public.cubi.bihealth.org/transient/varfish/anthenea/varfish-server-background-db-20210728-grch37-patch-20210728b.tar.gz>`__

Download and extract the file and mount it as ``/data`` inside the ``varfish-web`` container.
You can then apply the patch to your database with the following command.

::

    $ docker exec -it varfish-docker-compose_varfish-web_1 python /usr/src/app/manage.py \
        import_tables --tables-path /data --truncate --force

You can find out more details, give feedback, and ask for help `in this Github discussion <https://github.com/bihealth/varfish-server/discussions/451>`__.

----------------
v1.2.* to v2.*.*
----------------

**ClinVar Changes**
Please follow the instructions described in :ref:`admin_update_1_2_2_to_1_2_3` if you start at v1.2.1.

**In-House Background Database.**
A number of changes were made to the implementation of the background database.
The upgrade will re-create the in-house database as empty.

You will have to re-build the database manually with the command ``python manage.py rebuild_variant_summary``.
Assuming that you are running within ``varfish-docker-compose``, you can use the following command directly.

::

    $ docker exec -it varfish-docker-compose_varfish-web_1 python /usr/src/app/manage.py \
        rebuild_variant_summary

**Structural Variants.**
In case that the support for structural variants has been used, it is **strongly recommended** to re-annotate the structural variants with an updated version of ``varfish-annotator`` (v0.24 or above).
You will need to use ``varfish-cli`` in a recent version (v0.3.4 or above) for being able to import the data into VarFish.
Otherwise, see below for background and explanation on how to fill empty values in your database after upgrading the software an database to bollonaster.

In VarFish anthenea, the support for structural variants has been experimental only.
To prepare for improved support of structural variants, the database structure has been changed.
Prior, the number of carriers in the background had to be annotated outside of VarFish (in your pipeline).
This has changed now and VarFish can build a background database (and will do so weekly on sundays).

If you do not want to wait for next sunday to get your background database, you can force building a new background structural variant data set with:

::

    $ docker exec -it varfish-docker-compose_varfish-web_1 python /usr/src/app/manage.py \
        svs_bg_sv_set_build

New fields have been added for the proper representation of break-ends in VarFish.
They will only be properly filled after re-import of re-annotated data as described above.
You can fill the fields with reasonable values (that will work well for all cases except for breakends/BNDs where the connectivity of 3' and 5' ends cannot be properly detected without re-annotation) by using the following.

::

    $ docker exec -it varfish-docker-compose_varfish-web_1 python /usr/src/app/manage.py \
        svs_sv_fill_nulls

This is not strictly necessary and it is recommended to re-annotate and re-import.

.. _admin_update_1_2_2_to_1_2_3:

----------------
v1.2.2 to v1.2.3
----------------

**ClinVar Updates**
First, make sure that you have upgraded the data to ``20210728b`` following :ref:`admin_upgrade_data_release_20210728`.
Then, upgrade by just updating your ``varfish-docker-compose`` repository clone and calling ``docker-compose down && docker-compose up -d``.

Next, patch to data version ``20210728c`` using the following instructions.

We have made a larger change to the ClinVar database.
You will have to re-import the ClinVar database after upgrade follows.

Download the appropriate data patch from our file server:

GRCh37
    `varfish-server-background-db-20210728c-grch37.tar.gz <https://file-public.cubi.bihealth.org/transient/varfish/anthenea/varfish-server-background-db-20210728c-grch37.tar.gz>`__

GRCh38
    `varfish-server-background-db-20210728c-grch38.tar.gz <https://file-public.cubi.bihealth.org/transient/varfish/anthenea/varfish-server-background-db-20210728c-grch38.tar.gz>`__

Extract the output to a folder on your VarFish server, e.g., ``/data/varfish-data/varfish-server-background-db-20210728c-grch37``, such that this folder contains a file ``import_versions.tsv``.
Next, edit the ``docker-compose.yml`` file of your ``varfish-docker-compose`` such that the ``varfish-web`` entry's ``volumes`` field reads as follows.

::

    volumes:
      - "/data:/data:ro"

Then, restart VarFish by calling ``docker-compose down && docker-compose up -d``.
After startup, you can now do the following if you use GRCh37:

::

    docker exec -it varfish-docker-compose_varfish-web_1 python /usr/src/app/manage.py \
        import_tables --force --truncate --tables-path /data/varfish-server-background-db-20210728c-grch37 \
        --threads=0

If you use GRCh38, use

::

    docker exec -it varfish-docker-compose_varfish-web_1 python /usr/src/app/manage.py \
        import_tables --force --truncate --tables-path /data/varfish-server-background-db-20210728c-grch38 \
        --threads=0

This will import the ClinVar version from the 20210728 release in the fixed format compatible with ``v1.2.2``.
Note that this will also import a patch to the TAD data in

In case of any issues, contact us in the `Github Discussion <https://github.com/bihealth/varfish-server/discussions>`__ or directly by email.

------------------
v0.23.0 to v1.2.1
------------------

This includes all version in between, v0.23.1, ..., v1.2.1.

**Summary**

This are minor bug fix releases and small added features.
You should be able to upgrade by just updating your ``varfish-docker-compose`` repository clone and calling ``docker-compose up -d``.

------------------
v0.23.1 to v0.23.2
------------------

**Summary**

This is a minor bug fix release that improved the deployment of the VarFish Demo and Kiosk sites.
You should be able to upgrade by just updating your ``varfish-docker-compose`` repository clone and calling ``docker-compose up -d``.

------------------
v0.22.1 to v0.23.0
------------------

**Summary**

- The Docker Compose installer now provides support for setting up CADD score annotation via `cadd-rest-api <https://github.com/bihealth/cadd-rest-api>`__.
- The environment variable ``FIELD_ENCRYPTION_KEY`` **should** be setup properly by the user.
- Two new celery queues are needed: ``maintenance`` and ``export``.
- To enable the new and optional feature for uploading variants to SPANR you have to set the environment variable ``VARFISH_ENABLE_SPANR_SUBMISSION`` to ``1``.

Detailed Instructions
=====================

Docker Compose: cadd-rest-api
-----------------------------

Update your varfish-docker-compose installation with the changes from the Github repository without installing cadd-rest-api.
This will give you commented out lines for running one ``cadd-rest-api-server`` and multiple ``cadd-rest-api-celeryd-worker-?`` containers.
For enabling them, follow the instructions in :ref:`admin_extras_cadd_scripts`.

Additional Celery Queues
------------------------

After updating your ``varfish-docker-compose.yml`` file, ensure that you the two additional containers ``varfish-celeryd-maintenance`` and ``varfish-celeryd-export``.
These will run the background jobs for running maintenance tasks and export results.
They will be started when running ``docker-compose up``.

Environment Variable: ``FIELD_ENCRYPTION_KEY``
----------------------------------------------

Set the environment variable in the ``.env`` file as documented in :ref:`admin_config_misc`.
The default value is also stored in the public repository and thus not very secure.
