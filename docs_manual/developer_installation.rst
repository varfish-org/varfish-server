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

Please find the instructions for the Windows installation at the end of the page.

----------------
Install Postgres
----------------

Follow the instructions for your operating system to install `Postgres <https://www.postgresql.org>`_.
Make sure that the version is 12 (11, 13 and 14 would also work).
Ubuntu 20 already includes postgresql 12. In case of older Ubuntu versions, this would be::

    $ sudo apt install postgresql-12


Adapt the postgres configuration file, for postgres 14 this would be:

    sudo sed -i -e 's/.*max_locks_per_transaction.*/max_locks_per_transaction = 1024 # min 10/' /etc/postgresql/14/main/postgresql.conf

-------------
Install Redis
-------------

`Redis <https://redis.io>`_ is the broker that celery uses to manage the queues.
Follow the instructions for your operating system to install Redis.
For Ubuntu, this would be::

    $ sudo apt install redis-server

.. _dev_install_python_pipenv:

---------------------
Install Python Pipenv
---------------------

We use `pipenv <https://pipenv.pypa.io/en/latest/>`__ for managing dependencies.
The advantage over ``pip`` is that also the versions of "dependencies of dependencies" will be tracked in a ``Pipfile.lock`` file.
This allows for better reprocubility.
Earlier developer's instructions used ``conda`` but these instructions were updated.

Also, note that VarFish is developed using Python 3.10 only.
To install Python 3.10, you can use `pyenv <https://github.com/pyenv/pyenv>`__.
If you already have Python 3.10 (check with ``python --version`` then you can skip this step).

.. code-block:: bash

    $ git clone https://github.com/pyenv/pyenv.git ~/.pyenv
    $ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    $ echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    $ echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
    $ exec $SHELL
    $ pyenv install 3.10
    $ pyenv global 3.10

Now, install the latest version of pip and pipenv:

.. code-block:: bash

    $ pip install --upgrade pip pipenv


--------------------
Clone git repository
--------------------

Clone the VarFish Server repository and switch into the checkout.

.. code-block:: bash

    $ git clone https://github.com/bihealth/varfish-server
    $ cd varfish-server


---------------------------
Install Python Requirements
---------------------------

Some required packages have dependencies that are usually not preinstalled.
Therefore, run

.. code-block:: bash

    $ sudo bash utils/install_os_dependencies.sh

Now, you can install the Python dependencies as follows:

.. code-block:: bash

    $ pipenv install --dev

Afterwards, you can activate the virtual environment:

.. code-block:: bash

    $ pipenv shell
    # e.g.,
    $ make black

Alternatively, you can also run commands directly in the virtual environment:

.. code-block:: bash

    $ pipenv run make black

For greater verbosity, we will use ``pyenv run COMMAND`` below, but you can skip the ``pyenv run`` if you are in the ``pyenv shell``.

--------------
Setup Database
--------------

Use the tool provided in ``utils/`` to set up the database. The name for the
database should be ``varfish`` (create new user: yes, name: varfish, password: varfish).

.. code-block:: bash

    $ bash utils/setup_database.sh

------------
Setup vue.js
------------

Use the tool provided in ``utils/`` to set up vue.js.

.. code-block:: bash

    $ sudo bash utils/install_vue_dev.sh

Open an additional terminal and switch into the vue directory.
Then install the Varfish vue app.

.. code-block:: bash

    $ cd varfish/vueapp/
    $ npm install

When finished, keep this terminal open to run the vue app.

.. code-block:: bash

    $ npm run serve

-------------
Setup VarFish
-------------

First, create a ``.env`` file with the following content.

.. code-block:: bash

    export DATABASE_URL="postgres://varfish:varfish@127.0.0.1/varfish"
    export CELERY_BROKER_URL=redis://localhost:6379/0
    export PROJECTROLES_ADMIN_OWNER=root
    export DJANGO_SETTINGS_MODULE=config.settings.local

If you wish to enable structural variants, add the following line.

.. code-block:: bash

    export VARFISH_ENABLE_SVS=1

To create the tables in the VarFish database, run the ``migrate`` command.
This step can take a few minutes.

.. code-block:: bash

    $ pipenv run python manage.py migrate

Once done, create a superuser for your VarFish instance. By default, the VarFish root user is named ``root`` (the
setting can be changed in the ``.env`` file with the ``PROJECTROLES_ADMIN_OWNER`` variable).

.. code-block:: bash

    $ pipenv run python manage.py createsuperuser

Last, download the icon sets for VarFish and make scripts, stylesheets and icons available.

.. code-block:: bash

    $ pipenv run python manage.py geticons -c bi cil fa-regular fa-solid gridicons octicon
    $ pipenv run python manage.py collectstatic

When done, open two terminals and start the VarFish server and the celery server.

.. code-block:: bash

    terminal1$ pipenv run make serve
    terminal2$ pipenv run make celery


======================
Installation (Windows)
======================

The setup was done on a recent version of Windows 10 with Windows Subsystem for Linux Version 2 (WSL2).

-----------------
Installation WSL2
-----------------

Following [this tutorial](https://www.omgubuntu.co.uk/how-to-install-wsl2-on-windows-10) to install WSL2.

- Note that the whole thing appears to be a bit convoluted, you start out with `wsl.exe --install`
- Then you can install latest LTS Ubuntu 22.04 with the Microsoft Store
- Once complete, you probably end up with a WSL 1 (one!) that you can conver to version 2 (two!) with `wsl --set-version Ubuntu-22.04 2` or similar.
- WSL2 has some advantages including running a full Linux kernel but is even slower in I/O to the NTFS Windows mount.
- Everything that you do will be inside the WSL image.

--------------------
Install Dependencies
--------------------

.. code-block::

    $ sudo apt install libsasl2-dev python3-dev libldap2-dev libssl-dev gcc make rsync
    $ sudo apt install postgresql postgresql-server-dev-14 postgresql-client redis
    $ sudo service postgresql start
    $ sudo service postgresql status
    $ sudo service redis-server start
    $ sudo service redis-server status
    $ sudo sed -i -e 's/.*max_locks_per_transaction.*/max_locks_per_transaction = 1024 # min 10/' /etc/postgresql/14/main/postgresql.conf
    $ sudo service postgresql restart

Create a postgres user `varfish` with password `varfish` and a database.

.. code-block::

    $ sudo -u postgres createuser -s -r -d varfish -P
    $ [enter varfish as password]
    $ sudo -u postgres createdb --owner=varfish varfish

From here on, you can follow the instructions for the Linux installation, starting at `ref:dev_install_python_pipenv`.


-------------------------
Open WSL image in PyCharm
-------------------------

This has been tested with PyCharm Professional only.

- You can simply open projects in the WSL, e.g., `\\wsl$Ubuntu-22.04\home...`.
- You can add the interpreter in the `varfish-server` miniconda3 environment to PyCharm which gives you access to.
