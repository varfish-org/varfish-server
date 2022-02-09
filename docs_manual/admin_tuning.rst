.. _admin_tuning:

==================
Performance Tuning
==================

This chapter describes how to optimize the performance of VarFish and its components.
Mainly, this amounts to optimizing the hardware and software of the PostgreSQL server used by VarFish.
The audience of this chapter are those who have installed VarFish on their own infrastructure.

------------------
Selecting Hardware
------------------

Hardware selection is the most critical point.
The sizing of CPU and RAM is not so critical for VarFish.
16 CPU cores and 64 GB of RAM should be good to start with while more will not hurt and is not that expensive these days.
The focus should be in using a server with fast disk I/O.

From the author's experience the ideal build consists of

- multiple SSD disk,
- host bus adapter (as opposed to a RAID controller),
- using a ZFS setup.

The SSDs offer overall good throughput and excellent random I/O performance in particular.
They should appear as block devices (e.g., ``sda``) to the operating system such that ZFS can use them properly.
You will find that there is some discussion on the best setup of ZFS.
We have found ten SSDS in a single raidz2 pool with enabled compression (default) on the file system to offer excellent performance.
Further, up to two disks can fail without loss of data.

Of course, you can also use a classic hardware RAID controller.
We would advise against storing data on a SAN system and always recommend local disks (aka direct storage).
While VarFish will run fine in a virtual machine, you have to take good care that disk access is fast.
In particular, the QCOW driver of KVM is known to offer bad performance.

--------------------
Configuration Tuning
--------------------

The `varfish-docker-compose <https://github.com/bihealth/varfish-docker-compose>`__ repository contains a ``postgresql.conf`` file with pre-tuned database settings.
When using Docker Compose for your VarFish site you will get this configuration automatically.
This should be good enough for most instances.

Below are some proposals for starting points on tuning configuration.
Please consult the Postgres configuration documentation on all settings.
You will also find many resources on Postgres performance tuning on the internet using your favourite search engine.

**ZFS optimization.**
In the case that you store your database files on a ZFS file system you can try setting the ``full_page_writes`` setting to ``off``.
This will improve the write performance and according to various sources ZFS file systems are "torn page resilient" which prevents data loss.

::

    full_page_writes = off  # only do this on ZFS (!)

**SSD optimization.**
If you are using SSDs then you can adjust the value of ``random_page_cost``.
This value helps the Postgres query planner to estimate the cost of random vs. sequential data access.
For SSDs, you can set this to ``1.1``:

::

    random_page_cost = 1.1  # optimized for SSD

--------------------------
Placing Tables and Indices
--------------------------

In principle, you can the table space feature of PostgreSQL to move certain tables and indices to different storage classes.
The following tables and their indices are large and read-only after the initial import.

::

    conservation_knowngeneaa
    dbsnp_dbsnp
    frequencies_*
    extra_annos_*

Moving them to cheaper storage with higher latency than the rest of the data might be feasible if you are hard-pressed for saving storage.
The authors have not tried this and would be very interested in experience reports.

---------------
Reference Times
---------------

For reference, here are some timings for importing the background database on different hardware.

.. list-table:: Reference background data import times
    :header-rows: 1

    * - Data
      - VarFish
      - Postgres
      - Storage
      - File System
      - Time [HH:MM]
    * - 20210728-grch37
      - v0.23.9+42
      - 12.9
      - 25xSSD RBD 16.2.7
      - XFS
      - 13.5h
    * - 20210728-grch38
      - v0.23.9+42
      - 12.9
      - 25xSSD RBD 16.2.7
      - XFS
      - TBD
