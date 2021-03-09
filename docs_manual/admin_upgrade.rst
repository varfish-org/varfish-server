.. _admin_upgrade:

============================
Upgrade Varfish Installation
============================

This section contains upgrade instructions for upgrading your VarFish Server installation using `VarFish Docker Compose <https://github.com/bihealth/varfish-docker-compose>`__.

-------------------------------------
v0.22.1 to v0.23.0 (work in progress)
-------------------------------------

.. warning::

    Version v0.23.0 has not been released yet.
    We can only provide support once v0.23.0 has been officially released.

**Summary**

- The Docker Compose installer now provides support for setting up CADD score annotation via `cadd-rest-api <https://github.com/bihealth/cadd-rest-api>`__.
- The environment variable ``FIELD_ENCRYPTION_KEY`` **should** be setup properly.
- Two new celery queues are needed: ``maintenance`` and ``export``.

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
