.. _admin_config:

====================
System Configuration
====================

This section describes how to configure the ``varfish-docker-compose`` setup.
When running with the ``varfish-docker-compose`` files and the provided database files, VarFish comes preconfigured with sensible default settings and also contains some example datasets to try out.
There are a few things that you might want to tweak.
Please note that there might be more settings that you can change when exploring the VarFish source code but right now their use is not supported for external users.

.. _admin_config_tls:

-----------------------
TLS / SSL Configuration
-----------------------

In the ``docker-compose.yml`` file you will find sections starting with ``# BEGIN`` and are followed by a token, e.g., ``settings:testing``, ``settings:production-provide-certificate``, and ``settings:production-letsencrypt``.
You will have to decide for one of the following and make sure that the lines for your choice are not commented out while all the others should be (in the case of ``OR`` leave the section in for all ``OR``-ed settings).

The ``varfish-docker-compose`` setup uses `traefik <https://traefik.io/>`__ as a reverse proxy and must be reconfigured if you want to change the default behaviour of using self-signed certificates.

``settings:testing``
    By default (and as a fallback), traefik will use self-signed certificates that are recreated at every startup.
    These are probably fine for a test environment but you might want to change this to one of the below.
``settings:production-provide-certificate``
    You can provide your own certificates by placing them into ````config/traefik/tls/server.crt`` and ``server.key``.
    Make sure to provide the full certificate chain if needed (e.g., for DFN issued certificates).
``settings:production-letsencrypt``
      If your site is reachable from the internet then you can also use ``settings:production-letsencrypt`` which will use [letsencrypt](https://letsencrypt.org/) to obtain the certificates.
      NB: if you make your site reachable from the internet then you should be aware of the implications.
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

``VARFISH_LOGIN_PAGE_TEXT=``
    Text to display on the login page.
``FIELD_ENCRYPTION_KEY``
    Key to use for encrypting secrets in the database (such as saved public keys for the Beacon Site feature).
    You can generate such a key with the following command: ``python -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)))'``.

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

- CADD annotation (also needs adding this to docker-compose.yml)
- Kiosk Mode
- Updating Extras Data
