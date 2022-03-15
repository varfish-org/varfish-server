.. _admin_pap:

=================
PAP Configuration
=================

This section describes the setup of VarFish behind a PAP (package filter, application gateway, package filter) structure.

VarFish stores human genetic data which is by its very nature very privacy sensitives.
Administrators will thus want to set up VarFish in protected institution networks that are not accessible by the outside world.
However, certain data exchange is generally desired, such as connecting two or more VarFish instances with the clinical beacon protocol.

-------------
PAP Structure
-------------

In such cases, the German agency for information security (BSI) recommends the P-A-P structure (`link to 2021 edition of their recommendation <https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Grundschutz/Kompendium_Einzel_PDFs_2021/09_NET_Netze_und_Kommunikation/NET_3_2_Firewall_Edition_2021.html>`__).
The following figure illustrates the structure

.. figure:: figures/pap-structure.png
    :align: center
    :width: 80%

    Overview of VarFish server behind P-A-P structure.

The structure is as follows:

- A demilitarized zone (DMZ) network is setup to contain an application gateway.
  In the case of HTTP(S), this is a reverse proxy.
- Incoming traffic from the internet passes into the gateway passes through a packetfilter (in other words: firewall).
- Outgoing traffic out of the gateway passes another packetfilter and it then reaches the destination server in protected network.

The reasoning behind the structure is explained in the NET 3.2 document linked to above.
In the following section, we will explain the technical implementation.

--------------------------
Firewall and Network Setup
--------------------------

The German specification NET.3.2.A16 is as follows:

    **NET.3.2.A16 Aufbau einer "P-A-P" Struktur (S)**
    Eine "Paketfilter - Application-Level-Gateway - Paketfilter"-(P-A-P)-Struktur SOLLTE eingesetzt
    werden. Sie MUSS aus mehreren Komponenten mit jeweils dafür geeigneter Hard- und Software
    bestehen. Für die wichtigsten verwendeten Protokolle SOLLTEN Sicherheitsproxies auf
    Anwendungsschicht vorhanden sein. Für andere Dienste SOLLTEN zumindest generische
    Sicherheitsproxies für TCP und UDP genutzt werden. Die Sicherheitsproxies SOLLTEN zudem
    innerhalb einer abgesicherten Laufzeitumgebung des Betriebssystems ablaufen.

Which translates into English roughly as follows:

    **NET.3.2.A16 Creating a "P-A-P" Structure (S)**
    A "packet filter - application level gateway - packet filter"-(P-A-P)-Structure SHOULD be used.
    It MUST consist of multiple components with appropriate hardware and software.
    For the most important protocols, security proxies SHOULD exist on the application layer.
    For other services, at least generic security proxies for TCP and UDP SHOULD be used.
    The security proxies SHOULD run inside a secured runtime enviornment of the operating system.

A possible implementation looks as follows:

- The VarFish server runs in the internal network with IP ``10.0.10.10``.
- Create a separate VLAN for the PAP structure and use a /30 (or lower) CIDR prefix.
  Only place proxy services there, ideally only one.
    - Example: use ``1.2.3.0/30`` with IP gateway ``1.2.3.1`` and application gateway server ``1.2.3.2``.
- Configure the firewall to allow incoming traffic via HTTPS (TCP/443) to ``1.2.3.2`` only.
- Allow outgoing traffic from ``192.168.0.1`` via the packet filter to ``10.0.10.10`` via HTTPS (TCP/443) only.

The following section describes how to setup a Linux Docker container with the `traefik <https://traefik.io/>`__ reverse proxy.
To the authors' best understanding, this fulfills all of the required and optional rules for P-A-P by BSI.

---------------------------
Traefik Reverse Proxy Setup
---------------------------

Traefik is a versatile reverse proxy (and load balancer).
It works well with Docker but configuring it can be a bit daunting for beginners.
The following describes a straightforward and minimal setup.

Preparation:

1. Install a modern Linux server on the gateway server (``1.2.3.2`` from above)
2. On the server, install Docker `following the official instructions <https://docs.docker.com/get-docker/>`_
3. Also install Docker Compose `with the official instructinos <https://docs.docker.com/compose/install/>`_
4. Setup public DNS (e.g., ``varfish-ext.example.com``) to point to ``1.2.3.2`` and ensure that public resolvers can resolve it (e.g., Google DNS at ``8.8.8.8``)
5. We assume that your internal VarFish instance is available as ``varfish-int.example.com`` and it is setup with a valid TLS certificate.
6. Collect the public IPs of the hosts on the internet that you want to be able to access your VarFish instance.
   These might be cluster IPs if the remote servers are behind NAT.
   In the example below we use the sub network ``2.3.4.0/28`` and IP ``3.4.5.6`` as valid sources.

First, create some directories with the following command:

.. code-block:: terminal

    # mkdir -p /etc/reverse-proxy
    # mkdir -p /etc/reverse-proxy/var/traefik
    # mkdir -p /etc/reverse-proxy/etc/trafik
    # mkdir -p /etc/reverse-proxy/etc/trafik/conf.d

Now, create the file ``/etc/reverse-proxy/docker-compose.yaml`` as follows.

.. code-block:: yaml
    :caption: /etc/reverse-proxy/docker-compose.yaml

    version: "2"

    services:
      traefik:
        image: traefik:latest
        restart: always
        ports:
          - "443:443"
        networks:
          - web
        volumes:
          - ./var/traefik:/var/traefik:rw
          - ./etc/traefik:/etc/traefik:ro
        container_name: traefik

    networks:
      web:

This will create a new container named ``traefik`` with the latest version of Traefik.
The container goes into its own network and the port 443 is exposed.
The container can read ``/etc/reverse-proxy/traefik`` as ``/etc/traefik`` via a bind mount and read and write ``/etc/reverse-proxy/var/traefik`` as ``/var/traefik``.
The first will contain configuration, the latter will be used for storing letsencrypt certificate generation state

Next, create ``/etc/reverse-proxy/etc/traefik/traefik.yaml`` and ``/etc/reverse-proxy/etc/traefik/conf.d/dynamic_config.yaml``

.. code-block:: yaml
    :caption: /etc/reverse-proxy/etc/traefik/traefik.yaml

    entryPoints:
      websecure:
        address: ":443"

    providers:
      file:
        directory: /etc/traefik/conf.d
      docker:
        exposedByDefault: false

    certificatesResolvers:
      le:
        acme:
          email: youremail@example.com
          storage: /var/traefik/acme.json
          tlsChallenge: true

This will setup traefik correctly using letsencrypt certificate.

.. note::

    Regarding use of "legacy" technical language.
    Please note that the term ``ipwhitelist`` below is part of the traefik configuration syntax.
    We will update our documentation once updated terms are available.

.. code-block:: yaml
    :caption: /etc/reverse-proxy/etc/traefik/conf.d/dynamic_config.yaml

    # (1) TLS store
    tls:
      stores:
        default: {}

    http:
      # (2) set routing source for reverse proxy
      routers:
        varfish:
          middlewares:
            - varfish-add-prefix
            - varfish-ip-allowlist
          entryPoints:
            - websecure
          service: varfish
          rule: "Host(`varfish-ext.example.com`)"
          tls:
            certresolver: le
      # (3) routing destination for the reverse proxy
      services:
        varfish:
          loadBalancer:
            servers:
              - url: "https://varfish-int.bihealth.org"

      middlewares:
        # (4) expose only beaconsite endpoint
        varfish-add-prefix:
          addprefix:
            prefix: "/beaconsite/endpoint"
        varfish-ip-allowlist:
          ipwhitelist:
            sourcerange: "2.3.4.0/28,3.4.5.6"

This will setup the

1. TLS store for the certificates
2. routing source and
3. routing destination for the reverse proxy
4. automatically add ``/beaconsite/endpoint`` prefix so only the beaconsite endpoint is exposed, and
5. restrict access to the given source sites.

You can now startup the reverse proxy:

.. code-block::

    # cd /etc/reverse-proxy
    # docker-compose up -d

You can inspect the logs by using ``docker logs --tail=100 --follow traefik``.
You can increase the log verbosity by placing the following block on top of ``traefik.yaml``.

.. code-block:: yaml

    log:
      level: DEBUG
