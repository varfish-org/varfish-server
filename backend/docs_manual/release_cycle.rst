.. _release_cycle:

=============
Release Cycle
=============

This section documents the versioning and branching model of VarFish.
Generally, we follow the idea of release cycles as `also employed by Ceph <https://docs.ceph.com/en/latest/releases/general/>`__.

There is a new stable release every year, targeting the month of April.
Each stable release receives a name (e.g., "Anthenea") and a major release number, (e.g., 1 as "A" is the first letter of the alphabet).

Releases are named after starfish species.

Version numbers have three components, ``x.y.z``.
``x`` identifies the release cycle (e.g., ``1`` for ``Anthenea``).
``y`` identifies the release type:

- ``x.0.z`` - development versions (the bleeding edge)
- ``x.1.z`` - release candidates (for test users)
- ``x.2.z`` - stable/bugfix releases (for the general public)

-----------------------
Stable Releases (x.2.z)
-----------------------

There will be a new stable release per year ("x") with a small number of bug fixes and "trivial feature" releases ("z").
Stable releases will be supported for 14-16 months, so users have some time to upgrade

--------------------------
Release Candidates (x.1.z)
--------------------------

We will start feature freezes roughly a month before the next stable releases.
The release candidates are suitable for testing the

----------------------------
Development Versions (x.0.z)
----------------------------

These releases are suitable for sites that are involved in the development of Varfish themselves or that want to track the "bleeding edge" very closely.
The main developing sites (currently Berlin, Bonn) deploy self-built Docker containers from the current development branch.

-------------
Release Names
-------------

.. list-table::
    :header-rows: 1

    * - Year
      - Version
      - Release Name
      - Species
    * - 2022
      - 1.y.z
      - Anthenea
      - *Anthenea aspera*
    * - 2023
      - 2.y.z
      - Bollonaster
      - *Bollonaster pectinatus*
    * - 2024
      - 3.y.z
      - Culcita
      - *Culcita coriacea*
    * - 2025
      - 4.y.z
      - Doraster
      - *Doraster constellatus*
    * - 2026
      - 5.y.z
      - Euretaster
      - *Euretaster cibrosus*

----------------
Releases History
----------------

Starting with the 1.0.0 release.
