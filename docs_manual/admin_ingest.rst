.. _admin_ingest:

==================
Ingesting Variants
==================

This step describes how to ingest data into VarFish, that is

1. annotating variants and preparing them for import into VarFish
2. actually importing them into VarFish.

All of the steps below assume that you are running the Linux operating system.
It might also work on Mac OS but is curently unsupported.

------------------
Variant Annotation
------------------

In order to import a VCF file with SNVs and small indels, the file has to be prepared for import into VarFish server.
This is done using the Varfish Annotator software.

Installing the Annotator
========================

The VarFish Annotator is written in Java and you can find the JAR on `varfish-annotator Github releases page <https://github.com/bihealth/varfish-annotator/releases>`__.
However, it is recommended to install it via bioconda.
For this, you first have to install bioconda `as described in their manual <http://bioconda.github.io/user/install.html>`__.
Please ensure that you have the channels ``conda-forge``, ``bioconda``, and ``defaults`` set in the correct order as described in the bioconda installation manual.
A common pitfall is to forget the channel setup and subsequent failure to install ``varfish-annotator``.

The next step is to install the `varfish-annotator-cli package <http://bioconda.github.io/recipes/varfish-annotator-cli/README.html>`__ or create a conda environment with it.

.. code-block:: bash

    # EITHER
    $ conda install -y varfish-annotator-cli==0.14.0
    # OR
    $ conda create -y -n varfish-annotator varfish-annotator-cli==0.14.0
    $ conda activate varfish-annotator

As a side remark, you might consider installing ``mamba`` first and then using ``mamba install`` and ``create`` in favour of ``conda install`` and ``create``.

Obtaining the Annotator Data
============================

The downloaded archive has a size of ~10 GB while the extracted data has a size of ~55 GB.

.. code-block:: bash

    $ wget --no-check-certificate https://file-public.bihealth.org/transient/varfish/varfish-annotator-20201006.tar.gz{,.sha256}
    $ sha256sum --check varfish-annotator-20201006.tar.gz.sha256
    $ tar -xf varfish-annotator-20201006.tar.gz
    $ ls varfish-annotator-20201006 | cat
    hg19_ensembl.ser
    hg19_refseq_curated.ser
    hs37d5.fa
    hs37d5.fa.fai
    varfish-annotator-db-20201006.h2.db

Annotating VCF Files
====================

First, obtain some tests data for annotation and later import into VarFish Server.

.. code-block:: bash

    $ wget --no-check-certificate https://file-public.bihealth.org/transient/varfish/varfish-test-data-v0.22.2-20210212.tar.gz{,.sha256}
    $ sha256sum --check varfish-test-data-v0.22.2-20210212.tar.gz.sha256
    $ tar -xf varfish-test-data-v0.22.2-20210212.tar.gz.sha256

Next, you can use the ``varfish-annotator`` command:

.. code-block:: bash
    :linenos:

    $ varfish-annotator \
        -XX:MaxHeapSize=10g \
        -XX:+UseConcMarkSweepGC \
        annotate \
        --db-path varfish-annotator-20201006/varfish-annotator-db-20191129.h2.db \
        --ensembl-ser-path varfish-annotator-20201006/hg19_ensembl.ser \
        --refseq-ser-path varfish-annotator-20201006/hg19_refseq_curated.ser \
        --ref-path varfish-annotator-20201006/hs37d5.fa \
        --input-vcf "INPUT.vcf.gz" \
        --release "GRCh37" \
        --output-db-info "FAM_name.db_info.tsv" \
        --output-gts "FAM_name.gts.tsv" \
        --case-id "FAM_name"

Let us disect this call.
The first three lines contain the code to the wrapper script and some arguments for the ``java`` binary to allow for enough memory when running.

.. code-block:: bash
    :linenos:
    :lineno-start: 1

    $ varfish-annotator \
        -XX:MaxHeapSize=10g \
        -XX:+UseConcMarkSweepGC \

The next lines use the ``annotate`` sub command and provide the needed paths to the database files needed for annotation.
The ``.h2.db`` file contains information from variant databases such as gnomAD and ClinVar.
The ``.ser`` file are transcript databases used by the Jannovar library.
The ``.fa`` file is the path to the genome reference file used.
While only release GRCh37/hg19 is supported, using a file with UCSC-style chromosome names having ``chr`` prefixes would also work.

.. code-block:: bash
    :linenos:
    :lineno-start: 4
    :dedent: 0

        annotate \
        --db-path varfish-annotator-20201006/varfish-annotator-db-20191129.h2.db \
        --ensembl-ser-path varfish-annotator-20201006/hg19_ensembl.ser \
        --refseq-ser-path varfish-annotator-20201006/hg19_refseq_curated.ser \
        --ref-path varfish-annotator-20201006/hs37d5.fa \

The following lines provide the path to the input VCF file, specify the release name (must be ``GRCh37``) and the name of the case as written out.
This could be the name of the index patient, for example.

.. code-block:: bash
    :linenos:
    :lineno-start: 9
    :dedent: 0

        --input-vcf "INPUT.vcf.gz" \
        --release "GRCh37" \
        --case-id "index" \

The last lines

.. code-block:: bash
    :linenos:
    :lineno-start: 12
    :dedent: 0

        --output-db-info "FAM_name.db-info.tsv" \
        --output-gts "FAM_name.gts.tsv"

After the program terminates, you should create gzip files for the created TSV files and md5 sum files for them.

.. code-block:: bash

    $ gzip -c FAM_name.db-info.tsv >FAM_name.db-info.tsv.gz
    $ md5sum FAM_name.db-info.tsv.gz >FAM_name.db-info.tsv.gz.md5
    $ gzip -c FAM_name.gts.tsv >FAM_name.gts.tsv.gz
    $ md5sum FAM_name.gts.tsv.gz >FAM_name.gts.tsv.gz.md5

The next step is to import these files into VarFish server.
For this, a PLINK PED file has to be provided.
This is a tab-separated values (TSV) file with the following columns:

    1. family name
    2. individul name
    3. father name or ``0`` for founder
    4. mother name or ``0`` for founder
    5. sex of individual, ``1`` for male, ``2`` for female, ``0`` if unknown
    6. disease state of individual, ``1`` for unaffected, ``2`` for affected, ``0`` if unknown

For example, a trio would look as follows:

.. code-block::

    FAM_index   index       father  mother  2       2
    FAM_index   father      0       0       1       1
    FAM_index   mother      0       0       2       1

while a singleton could look as follows:

.. code-block::

    FAM_index   index       0       0       2       1

Note that you have to link family individuals with pseudo entries that have no corresponding entry in the VCF file.
For example, if you have genotypes for two siblings but none for the parents:

.. code-block::

    FAM_index   sister      father  mother  2       2
    FAM_index   broth       father  mother  2       2
    FAM_index   father      0       0       1       1
    FAM_index   mother      0       0       2       1

--------------
Variant Import
--------------

As a prerequisite you need to install the VarFish command line interface (CLI) Python app ``varfish-cli``.
You can install it from PyPi with ``pip install varfish-cli`` or from `Bioconda <http://bioconda.github.io/>`__ with ``conda install varfish-cli``.

Second, you need to create a new API token as described in :ref:`ui_api_tokens`.
Then, setup your Varfish CLI configuration file ``~/.varfishrc.toml`` as:

.. code-block:: toml

    [global]
    varfish_server_url = "https://varfish.example.com/"
    varfish_api_token = "XXX"

Now you can import the data that you imported above.
You will also find some example files in the ``test-data`` directory.

For the import you will also need the project UUID.
You can get this from the URLs in VarFish that list project properties.
The figure below shows this for the background job list but this also works for the project details view.

.. code-block:: bash

    $ varfish-cli --no-verify-ssl case create-import-info --resubmit \
        94777783-8797-429c-870d-c12bec2dd6ea \
        test-data/tsv/HG00102-N1-DNA1-WES1/*.{tsv.gz,.ped}

When executing the import as shown above, you have to specify:

- a pedigree file with suffix ``.ped``,
- a genotype annotation file as generated by ``varfish-annotator`` ending in ``.gts.tsv.gz``,
- a database info file as generated by ``varfish-annotator`` ending in ``.db-infos.tsv.gz``.

Optionally, you can also specify a TSV file with BAM quality control metris ending in ``.bam-qc.tsv.gz``.
Currently, the format is not properly documented yet but documentation and supporting tools are forthcoming.

Running the import command through VarFish CLI will create a background import job as shown below.
Once the job is done, the created or updated case will appear in the case list.

.. figure:: figures/admin/admin_import.png
    :align: center
    :width: 80%

------------
Undocumented
------------

The following needs to be properly documented here:

- Preparation of the BAM QC file that has the information about duplication rate etc.
  You can have a look at the ``*.bam-qc.tsv.gz`` files below the ``test-data`` directory.
