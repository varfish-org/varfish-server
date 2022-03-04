.. _api_overview:

=================
REST API Overview
=================

Varfish provides a growing set of REST APIs.
You can find an Python library for accessing the API and a command line interface in `varfish-cli <https://github.com/bihealth/varfish-cli>`_.

.. note::
    This documentation section is under development.

-------------
Using the API
-------------

Usage of the REST API is detailed in this section.
Basic knowledge of HTTP APIs is assumed.

Authentication
==============

The API supports authentication through Knox authentication tokens as well as logging in using your SODAR username and password.
Tokens are the recommended method for security purposes.

For token access, first retrieve your token using the **API Tokens** site app on the VarFish web UI.
Note that you can you only see the token once when creating it.

Add the token in the ``Authorization`` header of your HTTP request as follows:

.. code-block:: console

    Authorization: token 90c2483172515bc8f6d52fd608e5031db3fcdc06d5a83b24bec1688f39b72bcd

Versioning
==========

The VarFish REST API uses accept header versioning.
While specifying the desired API version in your HTTP requests is optional, it is **strongly recommended**.
This ensures you will get the appropriate return data and avoid running into unexpected incompatibility issues.

To enable versioning, add the ``Accept`` header to your request with the following media type and version syntax.
Replace the version number with your expected version.

Specific sections of the SODAR API may require their own accept header.
See the exact header requirement in the respective documentation on each section of the API.

Model Access and Permissions
============================

Objects in SODAR API views are accessed through their ``sodar_uuid`` field.

In the REST API documentation, *"UUID"* refers to the ``sodar_uuid`` field of each model unless otherwise noted.

For permissions the API uses the same rules which are in effect in the SODAR GUI.
That means you need to have appropriate project access for each operation.

Return Data
===========

The return data for each request will be a JSON document unless otherwise specified.

If return data is not specified in the documentation of an API view, it will return the appropriate HTTP status code along with an optional ``detail`` JSON field upon a successfully processed request.
