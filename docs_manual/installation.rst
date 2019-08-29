.. _installation:

============
Installation
============

---------------
Background Data
---------------

-----
Cases
-----

.. code:: bash

    python manage.py import_case \
        --case-name XXX \
        --index-name XXX \
        --path-ped XXX.ped \
        --path-genotypes XXX.gts.tsv.gz \
        --path-feature-effects XXX.feature-effects.tsv.gz \
        --path-db-info XXX.db-infos.tsv.gz \
        --project-uuid YYY
