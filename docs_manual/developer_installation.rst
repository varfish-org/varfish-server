.. _developer_installation:

============
Installation
============

The VarFish installation for developers should be set up differently from the
installation for production use.

The reason being is that the installation for production use runs completely in
a Docker environment. All containers are assigned to a Docker network that the
host by default has no access to, except for the reverse proxy that gives
access to the VarFish webinterface.

The developers installation is intended not to carry the full VarFish database
such that it is light-weight and fits on a laptop. We advise to install the
services not running in a Docker container.

--------------
Pre-requisites
--------------

This part describes how to install the software.

^^^^^^^^
Postgres
^^^^^^^^

Follow the instructions for your operating system to install `Postgres <https://www.postgresql.org>`_.
For Ubuntu, this would be::

    sudo apt install postgresql

^^^^^
Redis
^^^^^

`Redis <https://redis.io>`_ is the broker that celery uses to manage the queues.
Follow the instructions for your operating system to install Redis.
For Ubuntu, this would be::

    sudo apt install redis-server

^^^^^^^^^^^^^^^^^^^^
Clone git repository
^^^^^^^^^^^^^^^^^^^^

Clone the VarFish Server repository and switch into the checkout::

    $ git clone https://github.com/bihealth/varfish-server
    $ cd varfish-server

--------------
Setup Database
--------------

Use the tool provided in ``utility/`` to set up the database. The name for the
database should be ``varfish``::

    $ bash utility/setup_database.sh

-------------
Setup VarFish
-------------

To create the tables in the VarFish database, run the ``migrate`` command.
This step can take a few minutes::

    $ python manage.py migrate

Once done, create a superuser for your VarFish instance. By default, the VarFish root user is named ``root``::

    $ python manage.py createsuperuser

Last, download the icon sets for VarFish and make scripts, stylesheets and icons available::

    $ python manage.py geticons -c bi cil fa-regular fa-solid gridicons octicon
    $ python manage.py collectstatic
