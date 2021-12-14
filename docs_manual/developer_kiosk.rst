.. _developer_kiosk:

=====
Kiosk
=====

The Kiosk mode in VarFish enables users to upload VCF files.
This is not intended for production use as every upload will create it's own project, so there is no way of
organizing your cases properly. The mode serves only as a way to try out VarFish for external users.

-------------
Configuration
-------------

First, you need to download the VarFish annotator data (11Gb) and unpack it::

    $ wget https://file-public.bihealth.org/transient/varfish/varfish-annotator-20191129.tar.gz
    $ wget https://file-public.bihealth.org/transient/varfish/varfish-annotator-transcripts-20191129.tar.gz
    $ tar xzvf varfish-annotator-20191129.tar.gz
    $ tar xzvf varfish-transcripts-20191129.tar.gz

If you want to enable Kiosk mode, add the following lines to the ``.env`` file::

    export VARFISH_KIOSK_MODE=1
    export VARFISH_KIOSK_VARFISH_ANNOTATOR_REFSEQ_SER_PATH=/path/to/varfish-annotator-transcripts-20191129/hg19_refseq_curated.ser
    export VARFISH_KIOSK_VARFISH_ANNOTATOR_ENSEMBL_SER_PATH=/path/to/varfish-annotator-transcripts-20191129/hg19_ensembl.ser
    export VARFISH_KIOSK_VARFISH_ANNOTATOR_REFERENCE_PATH=/path/to/unpacked/varfish-annotator-20191129/hs37d5.fa
    export VARFISH_KIOSK_VARFISH_ANNOTATOR_DB_PATH=/path/to/unpacked/varfish-annotator-20191129/varfish-annotator-db-20191129.h2.db
    export VARFISH_KIOSK_CONDA_PATH=/path/to/miniconda/bin/activate

---
Run
---

To run the kiosk mode, simply (re)start the webserver server and the celery server::

    terminal1$ make serve
    terminal2$ make celery

