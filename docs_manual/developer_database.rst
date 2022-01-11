.. _developer_database:

===============
Database Import
===============

First, download the pre-build database files that we provide and unpack them.
Please make sure that you have enough space available. The packed file consumes
31 Gb. When unpacked, it consumed additional 188 Gb.

.. code-block:: bash

    $ cd /plenty/space
    $ wget https://file-public.bihealth.org/transient/varfish/varfish-server-background-db-20201006.tar.gz{,.sha256}
    $ sha256sum -c varfish-server-background-db-20201006.tar.gz.sha256
    $ tar xzvf varfish-server-background-db-20201006.tar.gz

We recommend to exclude the large databases: frequency tables, extra
annotations and dbSNP. Also, keep in mind that importing the whole database
takes >24h, depending on the speed of your HDD.

This is a list of the possible imports, sorted by its size:

===================  ====  ==================  =============================
Component            Size  Exclude             Function
===================  ====  ==================  =============================
gnomAD_genomes       80G   highly recommended  frequency annotation
extra-annos          50G   highly recommended  diverse
dbSNP                32G   highly recommended  SNP annotation
thousand_genomes     6,5G  highly recommended  frequency annotation
gnomAD_exomes        6,0G  highly recommended  frequency annotation
knowngeneaa          4,5G  highly recommended  alignment annotation
clinvar              3,3G  highly recommended  pathogenicity classification
ExAC                 1,9G  highly recommended  frequency annotation
dbVar                573M  recommended         SNP annotation
gnomAD_SV            250M  recommended         SV frequency annotation
ncbi_gene            151M                      gene annotation 
ensembl_regulatory   77M                       frequency annotation
DGV                  43M                       SV annotation
hpo                  22M                       phenotype information
hgnc                 15M                       gene annotation
gnomAD_constraints   13M                       frequency annotation
mgi                  10M                       mouse gene annotation
ensembltorefseq      8,3M                      identifier mapping
hgmd_public          5,0M                      gene annotation
ExAC_constraints     4,6M                      frequency annotation
refseqtoensembl      2,0M                      identifier mapping
ensembltogenesymbol  1,6M                      identifier mapping
ensembl_genes        1,2M                      gene annotation
HelixMTdb            1,2M                      MT frequency annotation
refseqtogenesymbol   1,1M                      identifier mapping
refseq_genes         804K                      gene annotation
mim2gene             764K                      phenotype information
MITOMAP              660K                      MT frequency annotation
kegg                 632K                      pathway annotation
mtDB                 336K                      MT frequency annotation
tads_hesc            108K                      domain annotation
tads_imr90           108K                      domain annotation
vista                104K                      orthologous region annotation
acmg                 16K                       disease gene annotation
===================  ====  ==================  =============================

You can find the ``import_versions.tsv`` file in the root folder of the
package. This file determines which component (called ``table_group`` and
represented as folder in the package) gets imported when the import command is
issued. To exclude a table, simply comment out (``#``) or delete the line.
Excluding tables that are not required for development can reduce time and
space consumption. Also, the GRCh38 tables can be excluded.

A space-consumption-friendly version of the file would look like this::

    build	table_group	version
    GRCh37	acmg	v2.0
    #GRCh37	clinvar	20200929
    #GRCh37	dbSNP	b151
    #GRCh37	dbVar	latest
    GRCh37	DGV	2016
    GRCh37	ensembl_genes	r96
    GRCh37	ensembl_regulatory	latest
    GRCh37	ensembltogenesymbol	latest
    GRCh37	ensembltorefseq	latest
    GRCh37	ExAC_constraints	r0.3.1
    #GRCh37	ExAC	r1
    #GRCh37	extra-annos	20200704
    GRCh37	gnomAD_constraints	v2.1.1
    #GRCh37	gnomAD_exomes	r2.1
    #GRCh37	gnomAD_genomes	r2.1
    #GRCh37	gnomAD_SV	v2
    GRCh37	HelixMTdb	20190926
    GRCh37	hgmd_public	ensembl_r75
    GRCh37	hgnc	latest
    GRCh37	hpo	latest
    GRCh37	kegg	april2011
    #GRCh37	knowngeneaa	latest
    GRCh37	mgi	latest
    GRCh37	mim2gene	latest
    GRCh37	MITOMAP	20200116
    GRCh37	mtDB	latest
    GRCh37	ncbi_gene	latest
    GRCh37	refseq_genes	r105
    GRCh37	refseqtoensembl	latest
    GRCh37	refseqtogenesymbol	latest
    GRCh37	tads_hesc	dixon2012
    GRCh37	tads_imr90	dixon2012
    #GRCh37	thousand_genomes	phase3
    GRCh37	vista	latest
    #GRCh38	clinvar	20200929
    #GRCh38	dbVar	latest
    #GRCh38	DGV	2016

To perform the import, issue:

.. code-block:: bash

    $ python manage.py import_tables --tables-path /plenty/space/varfish-server-background-db-20201006

Performing the import twice will automatically skip tables that are already
imported. To re-import tables, add the ``--force`` parameter to the command:

.. code-block:: bash

    $ python manage.py import_tables --tables-path varfish-db-downloader --force
