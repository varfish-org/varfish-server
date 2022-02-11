.. _admin_config:

====================
System Configuration
====================

This section describes how to configure the ``varfish-docker-compose`` setup.
When running with the ``varfish-docker-compose`` files and the provided database files, VarFish comes preconfigured with sensible default settings and also contains some example datasets to try out.
There are a few things that you might want to tweak.
Please note that there might be more settings that you can change when exploring the VarFish source code but right now their use is not supported for external users.

.. _admin_config_compose:

------------------------
VarFish & Docker Compose
------------------------

The recommended (and supported) way to deploy VarFish is using Docker compose.
The VarFish server and its component are not installed on the system itself but rather a number of Docker containers with fixed Docker images are run and work together.
The base ``docker-compose.yml`` file starts a fully functional VarFish server.
Docker Compose supports using so-called override files.

Basically, the mechanism works by providing an ``docker-compose.override.yml`` file that is automatically read at startup when running ``docker-compose up``.
This file is put into the `.gitignore` so it is not in the ``varfish-docker-compose`` repository but rather created in the checkouts (e.g., manually or using a configuration management tool such as Ansible).
On startup, Docker Compose will read first the base ``docker-compose.yml`` file.
It will then read the override file (if it exists) and recursively merge both YAML files with the override file overriding taking precedence over the base file.
Note that the recursive merging will be done on YAML dicts only, lists will overwritten.
The mechanism in detail is described in `the official documentation <https://docs.docker.com/compose/extends/>`__.

We provide the following files that you can use/combine into the local ``docker-compose.override.yml`` file of your installation.

- ``docker-compose.override.yml-cert`` -- use TLS encryption with your own certificate from your favourite certificate provider (by default an automatically generated self-signed certificate will be used by traefik, the reverse proxy).
- ``docker-compose.override.yml-letsencrypt`` -- use `letsencrypt <https://letsencrypt.org/>`__ to obtain a certificate.
- ``docker-compose.override.yml-cadd`` -- spawn Docker containers for allowing pathogenicity annotation of your variants with `CADD <https://cadd.kircherlab.bihealth.org/>`__.

The overall process is to copy any of the ``*.override.yml-*`` files to ``docker-compose.yml`` and adjusting it to your need (e.g., merging with another such file).

Note that you could also explicitely provide multiple override files but we do not consider this further.
For more information on the override mechanism see `the official documentation <https://docs.docker.com/compose/extends/>`__.

The following sections describe the possible adjustment with Docker Compose override files.

.. _admin_config_tls:

TLS / SSL Configuration
=======================

The ``varfish-docker-compose`` setup uses `traefik <https://traefik.io/>`__ as a reverse proxy and must be reconfigured if you want to change the default behaviour of using self-signed certificates.

Use the contents of ``docker-compose.override.yml-cert`` for providing your own certificate.
You have to put the cerver certificate and key into ``config/traefik/tls/server.crt`` and ``server.key`` and then restart the ``traefik`` container.
Make sure to provide the full certificate chain if needed (e.g., for DFN issued certificates).

If your site is reachable from the internet then you can also use the contents of ``docker-compose.override.yml-letsencrypt`` which will use [letsencrypt](https://letsencrypt.org/) to obtain the certificates.
Make sure to adjust the line with ``--certificatesresolvers.le.acme.email=`` to your email address.
Note well that if you make your site reachable from the internet then you should be aware of the implications.
VarFish is MIT licensed software which means that it comes "without any warranty of any kind", see the ``LICENSE`` file for details.

After changing the configuration, restart the site (e.g., with ``docker-compose down && docker-compose up -d`` if it is running in detached mode).

------------------
LDAP Configuration
------------------

VarFish can be configured to use up to two upstream LDAP servers (e.g., OpenLDAP or Microsoft Active Directory).
For this, you have to set the following environment variables in the file ``.env`` in your ``varfish-docker-compose`` checkout and restart the site.
The variables are given with their default values.

``ENABLE_LDAP=0``
    Enable primary LDAP authentication server (values: ``0``, ``1``).
``AUTH_LDAP_SERVER_URI=``
    URI for primary LDAP server (e.g., ``ldap://ldap.example.com:port`` or ``ldaps://...``).
``AUTH_LDAP_BIND_DN=``
    Distinguished name (DN) to use for binding to the LDAP server.
``AUTH_LDAP_BIND_PASSWORD=``
    Password to use for binding to the LDAP server.
``AUTH_LDAP_USER_SEARCH_BASE=``
    DN to use for the search base, e.g., ``DC=com,DC=example,DC=ldap``
``AUTH_LDAP_USERNAME_DOMAIN=``
    Domain to use for user names, e.g. with ``EXAMPLE`` users from this domain can login with ``user@EXAMPLE``.
``AUTH_LDAP_DOMAIN_PRINTABLE=${AUTH_LDAP_USERNAME_DOMAIN}``
    Domain used for printing the user name.

If you have the first LDAP configured then you can also enable the second one and configure it.

``ENABLE_LDAP_SECONDARY=0``
    Enable secondary LDAP authentication server (values: ``0``, ``1``).

The remaining variable names are derived from the ones of the primary server but using the prefix ``AUTH_LDAP2`` instead of ``AUTH_LDAP``.

------------------
SAML Configuration
------------------

Besides LDAP configuration, it is also possible to authenticate with existing SAML 2.0 ID Providers (e.g. Keycloak). Since varfish is built
on top of sodar core, you can also refer to the `sodar-core documentation <https://sodar-core.readthedocs.io/en/latest/app_projectroles_settings.html#saml-sso-configuration-optional>`__ for further help in configuring the ID Providers.

To enable SAML authentication with your ID Provider, a few steps are necessary. First, add a SAML Client for your ID Provider of choice. The sodar-core documentation features examples for Keycloak. Make sure you have assertion signing turned on and allow redirects to your varfish site.
The SAML processing URL should be set to the externally visible address of your varfish deployment, e.g. ``https://varfish.example.com/saml2_auth/acs/``.

Next, you need to obtain your metadata.xml aswell as the signing certificate and key file from the ID Provider. Make sure you convert these keys to standard OpenSSL
format, before starting your varfish instance (you can find more details `here <https://sodar-core.readthedocs.io/en/latest/app_projectroles_settings.html#saml-sso-configuration-optional>`__).
If you deploy varfish without docker, you can pass the file paths of your metadata.xml and key pair directly. Otherwise, make sure that you have included them
into a single folder and added the corresponding folder to your ``docker-compose.yml`` (or add it as a ``docker-compose-overrrided.yml``), like in the following snippet.

.. code-block:: yaml

    varfish-web:
      ...
      volumes:
        - "/path/to/my/secrets:/secrets:ro"

Then, define atleast the following variables in your docker-compose ``.env`` file (or the environment variables when running the server natively).

``ENABLE_SAML``
    [Default 0] Enable [1] or Disable [0] SAML authentication
``SAML_CLIENT_ENTITY_ID``
    The SAML client ID set in the ID Provider config (e.g. "varfish")
``SAML_CLIENT_ENTITY_URL``
    The externally visible URL of your varfish deployment
``SAML_CLIENT_METADATA_FILE``
    The path to the metadata.xml file retrieved from your ID Provider. If you deploy using docker, this must be a path inside the container.
``SAML_CLLIENT_IDP``
    The url to your IDP. In case of keycloak it can look something like https://keycloak.example.com/auth/realms/<my_varfish_realm>
``SAML_CLIENT_KEY_FILE``
    Path to the SAML signing key for the client.
``SAML_CLIENT_CERT_FILE``
    Path to the SAML certificate for the client.
``SAML_CLIENT_XMLSEC1``
    [Default /usr/bin/xmlsec1] Path to the xmlsec executable.

By default, the SAML attributes map is configured to work with Keycloak as SAML Auth provider. If you are using a different ID Provider,
or different settings you also need to adjust the ``SAML_ATTRIBUTES_MAP`` option.

``SAML_ATTRIBUTES_MAP``
    A dictionary identifying the SAML claims needed to retrieve user information. You need to set atleast ``email``, ``username``, ``first_name`` and ``last_name``. Example: ``SAML_ATTRIBUTES_MAP="email=email,username=uid,first_name=firstName,last_name=name"``

To set initial user permissions on first login, you can use the following options:

``SAML_NEW_USER_GROUPS``
    Comma separated list of groups for a new user to join.
``SAML_NEW_USER_ACTIVE_STATUS``
    [Default True] Whether a new user is considered active.
``SAML_NEW_USER_STAFF_STATUS``
    [Default True] New users get the staff status.
``SAML_NEW_USER_SUPERUSER_STATUS``
    [Default False] New users are marked superusers (I advise leaving this one alone).

If you encounter any troubles with this rather involved procedure, feel free to take a look at the discussion forums on `github <https://github.com/bihealth/varfish-server/discussions>`__ and open a thread.

-----------------
Sending of Emails
-----------------

You can configure VarFish to send out emails, e.g., when permissions are granted to users.

``PROJECTROLES_SEND_EMAIL=0``
    Enable sending of emails.
``EMAIL_SENDER=``
    String to use for the sender, e.g., ``noreply@varfish.example.com``.
``EMAIL_SUBJECT_PREFIX=``
    Prefix to use for email subjects, e.g., ``[VarFish]``.
``EMAIL_URL=``
    URL to the SMTP server to use, e.g., ``smtp://user:password@mail.example.com:1234``.

------------------------
External Postgres Server
------------------------

In some setups, it might make sense to run your own Postgres server.
The most common use case would be that you want to run VarFish in a setting where fast disks are not available (virtual machines or in a "cloud" setting).
You might still have a dedicated, fast Postgres server running (or available as a service from your cloud provider).
In this case, you can configure the database connection settings as follows.

``DATABASE_URL=postgresql://postgres:password@postgres/varfish``
    Adjust to the credentials, server, and database name that you want to use.

The default settings do not make for secure settings in the general case.
However, Docker Compose will create a private network that is only available to the Docker containers.
In the default ``docker-compose`` setup, postgres server is thus not exposed to the outside and only reachable by the VarFish web server and queue workers.

.. _admin_config_misc:

---------------------------
Miscellaneous Configuration
---------------------------

``VARFISH_LOGIN_PAGE_TEXT``
    Text to display on the login page.
``FIELD_ENCRYPTION_KEY``
    Key to use for encrypting secrets in the database (such as saved public keys for the Beacon Site feature).
    You can generate such a key with the following command: ``python -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)))'``.
``VARFISH_QUERY_MAX_UNION``
    Maximal number of cases to query for at the same time for joint queries.
    Default is ``20``.

--------------------
Sentry Configuration
--------------------

`Sentry <https://sentry.io/welcome/>`__ is a service for monitoring web apps.
Their open source version can be installed on premise.
You can configure sentry support as follows

``ENABLE_SENTRY=0``
    Enable Sentry support.
``SENTRY_DSN=``
    A sentry DSN to report to.
    See Sentry documentation for details.

----------------------------------
System and Docker (Compose) Tweaks
----------------------------------

A number of customizations customizations of the installation can be done using Docker or Docker Compose.
Other customizations have to be done on the system level.
This section lists those that the authors are aware of but in particular network-related settings can be done on many levels.

Using Non-Default HTTP(S) Ports
===============================

If you want to use non-standard HTTP and HTTPS ports (defaults are 80 and 443) then you can tweak this in the ``traefik`` container section.
You have to adjust two parts, below we give them separately with full YAML "key" paths.

.. code-block:: yaml

    services:
      traefik:
        ports:
          - "80:80"
          - "443:443"

To listen on ports ``8080`` and ``8443`` instead, your override file should have:

    services:
      traefik:
        ports:
          - "8080:80"
          - "8443:443"

Also, you have to adjust the command line arguments to traefik for the ``web`` (HTTP) and ``websecure`` (HTTPS) entrypoints.

.. code-block:: yaml

    services:
      traefik:
        command:
          # ...
          - "--entrypoints.web.address=:80"
          - "--entrypoints.websecure.address=:443"

Use the following in your override file.

.. code-block:: yaml

    services:
      traefik:
        command:
          # ...
          - "--entrypoints.web.address=:8080"
          - "--entrypoints.websecure.address=:8443"

Based on the ``docker-compose.yml`` file alone, your ``docker-compose.override.yml`` file should contain the following line.
You will have to adjust the file accordingly if you want to use a custom static certificate or letsencrypt by incorporating the files from the provided example ``docker-compose.override.yml-*`` files.

.. code-block:: yaml

    services:
      traefik:
        ports:
          - "8080:80"
          - "8443:443"
        command:
          - "--providers.docker=true"
          - "--providers.docker.exposedbydefault=false"
          - "--entrypoints.web.address=:80"
          - "--entrypoints.web.http.redirections.entryPoint.to=websecure"
          - "--entrypoints.web.http.redirections.entryPoint.scheme=https"
          - "--entrypoints.web.http.redirections.entrypoint.permanent=true"
          - "--entrypoints.web.address=:80"
          - "--entrypoints.websecure.address=:443"

Then, restart by calling ``docker-compose up -d`` in the directory with the ``docker-compose.yml`` file.

Listing on Specific IPs
=======================

By default, the ``traefik`` container will listen on all IPs and interfaces of the host machine.

You can change this by prefixing the ``ports`` list with the IPs to listen on.
The settings to adjust here are:

.. code-block:: yaml

    services:
      traefik:
        ports:
          - "80:80"
          - "443:443"

And they need to be overwritten as follows in your override file.

.. code-block:: yaml

    services:
      traefik:
        ports:
          - "10.0.0.1:80:80"
          - "10.0.0.1:443:443"

More details can be found in the `corresponding section of the Docker Compose manual <https://docs.docker.com/compose/compose-file/compose-file-v3/#ports>`_.
Of course, you can combine this with adjusting the ports, e.g., to ``10.0.0.1:8080:80`` etc.

Limit Incoming Traffic
======================

In some settings you might want to limit incoming traffic to certain networks / IP ranges.
In principle, this is possible with adjusting the Traefik load balancer/reverse proxy.
However, we would recommend you to use the firewall of your operating system or your overall network for this purpose.
Consult the corresponding manual (e.g., of ``firewalld`` for CentOS/Red Hat or of ``ufw`` for Debian/Ubuntu) for instructions.
We remark that in most cases it is better to perform an actual separation of networks and place each (virtual) machine into one network only.

---------------------
Understanding Volumes
---------------------

The ``volumes`` sub directory of the ``varfish-docker-compose`` directory contains the data for the containers.
These are as follows.

``cadd-rest-api``
    Databases for variant annotation with CADD (large).

``exomiser``
    Databases for variant prioritization (medium)

``jannovar``
    Transcript databases for annotation (small).

``minio``
    Storage for files uploaded from client via REST API (big).

``postgres``
    PostgreSQL databases (very big).

``redis``
    Storage for the work queues (small).

``traefik``
    Configuration and certificates for load balancer (very small).

In principle, you can put these on different storages systems (e.g., some over the network and some on directly attached disks).
The main motivation is that fast storage is expensive.
Putting the small and medium sized directories on slower, cheaper storage will have little or no effect on storage efficiency.
At the same time, access to ``redis`` and ``exomiser`` directories should be fast.
As for ``postgres``, this storage is accessed most heavily and should be on storage as fast as you can afford.
``cadd-rest-api`` should also be on fast storage but it is accessed almost only read-only.
You can put the ``minio`` folder on slower storage to shave off some storage costs from your VarFish installation.

To summarize:

- You can put ``minio`` on cheaper storage.
- As for ``cadd-rest-api``, you can probably get away to put this on cheaper storage.
- Put everything else, in particular ``postgres`` on storage as fast as you can afford.

As described in the section :ref:`admin_tuning`, the authors recommend using an advanced file system such as ZFS on multiple SSDs for large, fast storage and enabling compression.
You will get excellent performance and can expect storage saving of 50%.

--------------------------
Beacon Site (Experimental)
--------------------------

An experimental support for the GA4GH beacon protocol.

``VARFISH_ENABLE_BEACON_SITE=``
    Whether or not to enable experimental beacon site support.

--------------------------
Undocumented Configuration
--------------------------

The following list remains a points to implement with Docker Compose and document.

- Kiosk Mode
- Updating Extras Data
