.. _api_beacon:

==============================
Clinical GA4GH Beacon Protocol
==============================

This section describes the "Clinical Beacon" protocol version 1 ("Clinical Beacon v1").
It follows the `GA4GH Beacon Protocol v1 <https://beacon-project.io/>`__ ("Beacon v1") in large parts with slight deviations.
The end points and payloads are the same as in Beacon v1.
However, we add two important features, as explained below.

1. The client sends the current user in the ``X-Beacon-User`` header.
2. The client has to sign the ``X-Beacon-User`` and ``Date`` HTTP headers using the `Signing HTTP Messages <https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures-12>`__ IETF draft.

You can find a simple Python implementation of a standalone client `on Github <https://github.com/bihealth/varfish-clinical-beacon-client>`__.

------------------------
``X-Beacon-User`` Header
------------------------

The GA4GH Beacon v1 protocol is meant to be used in a "zero trust" environment and they specify that `authentication is done using OAuth2 <https://github.com/ga4gh-beacon/specification/blob/master/beacon.md#security>`__.
In an ideal world, VarFish sites having installed VarFish would be able to connect to local OpenID instances.
In reality, many sites will be seated in clinical environments where Microsoft ActiveDirectory is used for authentication and Microsoft Federated Services use SAML instead.

Further, VarFish sites connecting to each other will have real-world paper contracts for data exchange agreements and after signing such contracts they can trust each other.
In the first version we thus decided not to implement zero trust concepts.

The client thus has to set the ``X-Beacon-User`` header to a string that identifies the querying user uniquely.
It is the decision of the client whether it uses interpretable user names or for the sake of user data security, it can use pseudonyms.
This is left to the discretion of the implementing sites and contract partners.
VarFish currently implements this by sending the clear text user names.

---------------
``Date Header``
---------------

This is a standard HTTP header that is mandatory in the Clinical Beacon v1 protocol.

--------------
Header Signing
--------------

We use the `Signing HTTP Messages <https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures-12>`__ IETF draft for signing HTTP requests.
The signature header will typically look as follows (without wrapping of course):

::

    Signature keyId="org.bihealth.varfish",algorithm="rsa-sha512",headers="date x-beacon-user",\
    signature="mxY7+9vizRbO7mUJVyvxXm3VgpYycQWNulrAafMOWJ29WYQYMf2i5PBPP3jYBhIGd/3zZ+x+mlQw8xEw\
    M6UWvE3QRqzlzBE0ZHeWKgX4h11N1MhtXTnhXL9CL/VqbcgbBI9trkwB/xxaXhUOpvavA37J1ljrdTbXhghCHZ65hMi\
    04fUnKKkFhuwOzZ6N5/amIuizc2JeDe73Pg+D5HA4AnE2bnCmf8AqhKLd434SdchcYAHqYTJaxBA2Pxngerg6oSenli\
    rgukzrBdbdRpvnFFtQzZsQ56v9hS8cqF/phtl+isAT/dcwvO9/lCKaf3QE8YKCcQmDnPJiQLdtQ9mZKw==",\
    created="1646407724"'

Where

- ``keyId`` is the ID of the key pair used for signing
- ``algorithm`` is the algorithm that has been used for generating the key pair
- ``headers`` is the space-separated list of headers that are signed (must be ``date x-beacon-user``)
- ``signature`` is the Base 64 encoded signature.

This leaves open the question for generating the key.
We use standard RSA and ECDSA keys, Varfish supports the following algorithms:

- ``rsa-sha256``
- ``rsa-sha512``
- ``ecdsa-sha256``
- ``ecdsa-sha256``

The `standalone client on Github <https://github.com/bihealth/varfish-clinical-beacon-client>`__ provides examples for key generation.

Key exchange is trivial as only the public key needs to be registered by the server but it also **must** be registered by the server before making any query.

-------------
Final Remarks
-------------

Thus, the Clinical Beacon Protocol v1 is equal to the GA4GH Beacon Protocol v1 with the exception that:

- sites are expected to have a certain level of trust as they share non-public data,
- sites send a string with each query to identify the querying user, and
- all queries are signed with public/private key pairs and each client first needs to register with each server by sending its public key.

As a final remark, API endpoints should of course be deployed behind HTTPS but that is out of scope here.
