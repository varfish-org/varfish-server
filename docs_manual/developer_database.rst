.. _developer_database:

===============
Database Import
===============

To prepare the VarFish database, follow `the instructions for the VarFish DB Downloader <https://github.com/bihealth/varfish-db-downloader>`_.
Downloading and processing the data can take multiple days.

The VarFish DB Downloader working folder consumes 1.7Tb for GRCh37 and 5.4Tb for GRCh38.
The pre-computed tables for VarFish consume 208Gb and the final
postgres database consumes 500Gb. Please make sure that there is enough free
space available. However, we recommend to exclude the large databases:
Frequency tables, extra annotations and dbSNP. Also, keep in mind that
importing the whole database takes >24h, depending on the speed of your HDD.

In the future, we plan to provide a pre-build package for import.

This is a list of the possible imports, sorted by its size:

===================  ====  ==================  ===================================
Component            Size  Exclude             Function
===================  ====  ==================  ===================================
gnomAD_genomes       80G   highly recommended  frequency annotation
extra_annos          57G   highly recommended  diverse
dbSNP                56G   highly recommended  SNP annotation
gnomAD_exomes        6.0G  highly recommended  frequency annotation
knowngeneaa          4.5G  highly recommended  multiz alignment of 100 vertebrates
clinvar              2.4G  highly recommended  pathogenicity classification
ExAC                 1.9G  highly recommended  frequency annotation
dbVar                623M  recommended         SNP annotation
thousand_genomes     312M  recommended         frequency annotation
gnomAD_SV            218M  recommended         SV frequency annotation
DGV                  88M   yes, import broken  SV annotation
ensembl_regulatory   68M   yes, import broken  frequency annotation
gnomAD_constraints   13M   yes, import broken  frequency annotation
ensembltorefseq      8.6M                      identifier mapping
hgmd_public          6.3M  yes, import broken  gene annotation
ExAC_constraints     4.8M  yes, import broken  frequency annotation
hgnc                 3.3M  yes, import broken  gene annotation
ensembltogenesymbol  1.8M  yes, import broken  identifier mapping
ensembl_genes        1.3M                      gene annotation
HelixMTdb            1.1M  yes, import broken  MT frequency annotation
MITOMAP              1.1M  yes, import broken  MT frequency annotation
refseq_genes         1.1M                      gene annotation
mtDB                 514K  yes, import broken  MT frequency annotation
tads_hesc            258K                      domain annotation
tads_imr90           258K                      domain annotation
===================  ====  ==================  ===================================

You can find the ``import_versions.tsv`` file in the root folder of the
package. This file determines which component (called ``table_group`` and
represented as folder in the package) gets imported when the import command is
issued. To exclude a table, simply comment out (``#``) or delete the line.
Excluding tables that are not required for development can reduce time and space
consumption.

A space-consumption-friendly version of the file would look like this::

    build   table_group version
    #GRCh37 clinvar 20210728
    #GRCh37 dbSNP   b155
    #GRCh37 dbVar   20210728
    #GRCh37  DGV 2016
    #GRCh37  DGV 2020
    GRCh37  ensembl_genes   r104
    #GRCh37  ensembl_regulatory  20210728
    GRCh37  ensembltogenesymbol 20210728
    #GRCh37  ensembltorefseq 20210728
    #GRCh37 ExAC    r1
    #GRCh37  ExAC_constraints    r0.3.1
    #GRCh37 extra_annos 20210728
    #GRCh37  gnomAD_constraints  v2.1.1
    #GRCh37 gnomAD_exomes   r2.1.1
    #GRCh37 gnomAD_genomes  r2.1.1
    #GRCh37 gnomAD_SV   v2.1
    #GRCh37  HelixMTdb   20200327
    #GRCh37  hgmd_public ensembl_r104
    #GRCh37  hgnc    20210728
    #GRCh37 knowngeneaa 20210728
    #GRCh37  MITOMAP 20210728
    #GRCh37  mtDB    20210728
    GRCh37  refseq_genes    r105
    GRCh37  tads_hesc   dixon2012
    GRCh37  tads_imr90  dixon2012
    #GRCh37 thousand_genomes    phase3
    #GRCh37  vista   20210728

To perform the import, issue::

    $ python manage.py import_tables --tables-path varfish-db-downloader

Performing the import twice will automatically skip tables that are already imported.
To re-import tables, add the ``--force`` parameter to the command::

    $ python manage.py import_tables --tables-path varfish-db-downloader --force

