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

----------------
Install Postgres
----------------

Follow the instructions for your operating system to install `Postgres <https://www.postgresql.org>`_.
For Ubuntu, this would be::

    sudo apt install postgresql

-------------
Install Redis
-------------

`Redis <https://redis.io>`_ is the broker that celery uses to manage the queues.
Follow the instructions for your operating system to install Redis.
For Ubuntu, this would be::

    sudo apt install redis-server

-----------------
Install miniconda
-----------------

miniconda helps to set up encapsulated Python environments.
This step is optional. You can also use pipenv, but to our experience,
resolving the dependencies in pipenv is terribly slow::

    $ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    $ bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3
    $ source ~/miniconda3/bin/activate
    $ conda init
    $ conda create -n varfish python=3.8 pip
    $ conda activate varfish

--------------------
Clone git repository
--------------------

Clone the VarFish Server repository and switch into the checkout::

    $ git clone https://github.com/bihealth/varfish-server
    $ cd varfish-server


---------------------------
Install Python Requirements
---------------------------

With the conda/Python environment activated, install all the requirements::

    $ for i in requirements/*; do install -r $i; done

--------------
Setup Database
--------------

Use the tool provided in ``utility/`` to set up the database. The name for the
database should be ``varfish``::

    $ bash utility/setup_database.sh

-------------
Setup VarFish
-------------

First, create a ``.env`` file with the following content::

    export DATABASE_URL="postgres://varfish:varfish@127.0.0.1/varfish"
    export CELERY_BROKER_URL=redis://localhost:6379/0
    export PROJECTROLES_ADMIN_OWNER=root
    export DJANGO_SETTINGS_MODULE=config.settings.local

If you wish to enable structural variants, add the following line::

    export VARFISH_ENABLE_SVS=1

To create the tables in the VarFish database, run the ``migrate`` command.
This step can take a few minutes::

    $ python manage.py migrate

Once done, create a superuser for your VarFish instance. By default, the VarFish root user is named ``root`` (the
setting can be changed in the ``.env`` file with the ``PROJECTROLES_ADMIN_OWNER`` variable)::

    $ python manage.py createsuperuser

Last, download the icon sets for VarFish and make scripts, stylesheets and icons available::

    $ python manage.py geticons -c bi cil fa-regular fa-solid gridicons octicon
    $ python manage.py collectstatic

When done, open two terminals and start the VarFish server and the celery server::

    terminal1$ make server
    terminal2$ make celery
