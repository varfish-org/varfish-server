.. _admin_backup:

============
Data Backups
============

This section describes how to create data backups in VarFish.
The assumption is that you are running VarFish in the recommended way via Docker Compose.

All valuable state is kept in the VarFish PostgreSQL database.
VarFish provides a convenient way to call the PostgreSQL tool ``pg_dump``.

You can call it in the following way when VarFish is running under Docker Compose and the postgres container is running as well.

::

    # docker exec -it varfish-docker-compose_varfish-web_1 \
        python /usr/src/app/manage.py pg_dump --mode=MODE

This will execute ``python /usr/src/app/manage.py pg_dump --mode=MODE`` in the docker container that is running the VarFish web server.

You can use one of the following dump modes.

``full``
    This will perform a full data dump including all background data.

``backup-large``
    This will exclude the huge background data tables, e.g., dbSNP and gnomAD.

``backup-small``
    This will also exclude all imported variant data.
    The assumption is that you have a separate backup of the imported TSV files or can easily regenerate them from the VCF files that you still have.

Here is an example on how to create a compressed "small" dump file named ``varfish-${day_of_week}.sql.gz`` such that you get a rotating daily dump.

::

    # docker exec -it varfish-docker-compose_varfish-web_1 \
        python /usr/src/app/manage.py pg_dump --mode=MODE \
      | gzip -c \
      > varfish-$(date +%a).sql.gz

