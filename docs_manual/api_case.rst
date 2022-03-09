.. _api_case:

================
Case & Query API
================

The REST API for case access and is described in this section.
Cases are not managed directly but through the :ref:`api_importer`.


----------
Versioning
----------

For accept header versioning, the following media type and version are expected in the current VarFish version:

.. code-block:: console

    Accept: application/vnd.bihealth.varfish+json; version=0.23.9


-----------
Return Data
-----------

The return data for each request will be a JSON document unless otherwise
specified.

If return data is not specified in the documentation of an API view, it will
return the appropriate HTTP status code along with an optional ``detail`` JSON
field upon a successfully processed request.

For creation views, the ``sodar_uuid`` of the created object is returned
along with other object fields.

--------------
Query Settings
--------------

The query follows a :ref:`JSON Schema <api_json_schemas>`.

---------
API Views
---------

.. currentmodule:: variants.views_api

.. autoclass:: CaseListApiView

.. autoclass:: CaseRetrieveApiView

.. autoclass:: SmallVariantQueryApiView

.. autoclass:: SmallVariantQueryCreateApiView

.. autoclass:: SmallVariantQueryRetrieveApiView

.. autoclass:: SmallVariantQueryStatusApiView

.. autoclass:: SmallVariantQueryUpdateApiView

.. autoclass:: SmallVariantQueryFetchResultsApiView

.. autoclass:: SmallVariantQuerySettingsShortcutApiView
