.. _admin_upgrade:

============================
Upgrade Varfish Installation
============================

This section contains upgrade instructions for upgrading your VarFish Server installation using `VarFish Docker Compose <https://github.com/bihealth/varfish-docker-compose>`__.

------------------
v0.23.0 to v0.23.9
------------------

This includes all version in between, v0.23.1, ..., v0.23.9.

**Summary**

This are minor bug fix releases.
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
