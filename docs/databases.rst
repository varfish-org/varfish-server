.. _databases:

=========
Databases
=========

This sections gives information about the integrated databases and tools and the ones that are linked out to.
Further, it provides some pointers towards how to extend VarFish's database and tool collection.

------------------------------
Integrated Databases and Tools
------------------------------

The following databases are integrated into VarFish, meaning that their contents are available from within VarFish itself.

+-------------------+---------------------------+
|     Category      |         Database          |
+===================+===========================+
| Frequency         | gnomAD                    |
+-------------------+---------------------------+
|                   | ExAC                      |
+-------------------+---------------------------+
|                   | 1000 Genomes              |
+-------------------+---------------------------+
|                   | mtDB                      |
+-------------------+---------------------------+
|                   | helixMTdb                 |
+-------------------+---------------------------+
|                   | MITOMAP                   |
+-------------------+---------------------------+
| Clinical          | ClinVar                   |
+-------------------+---------------------------+
|                   | HGMD Public               |
+-------------------+---------------------------+
| Variant Database  | dbSNP                     |
+-------------------+---------------------------+
| Variant Tools     | VariantValidator          |
+-------------------+---------------------------+
| Phenotype         | HPO                       |
+-------------------+---------------------------+
|                   | OMI                       |
+-------------------+---------------------------+
|                   | MGI Mapping               |
+-------------------+---------------------------+
| Gene Description  | HGNC                      |
+-------------------+---------------------------+
|                   | NCBI Gene Summary         |
+-------------------+---------------------------+
|                   | NCBI GeneRIF              |
+-------------------+---------------------------+
|                   | ACMG Recommendations Gene |
+-------------------+---------------------------+
|                   | HPO                       |
+-------------------+---------------------------+
| Pathways          | KEGG                      |
+-------------------+---------------------------+
| Constraint Scores | gnomAD pLI/LOEUF          |
+-------------------+---------------------------+
|                   | ExAC pLI                  |
+-------------------+---------------------------+
| Conservation      | UCSC 100 Vertebrates      |
+-------------------+---------------------------+


----------------------------
Link-Out Databases and Tools
----------------------------

VarFish links out to the following databases and tools.

+--------------------+-----------------------+
|      Category      |       Database        |
+====================+=======================+
| Gene               | OMIM                  |
+--------------------+-----------------------+
|                    | GeneCards             |
+--------------------+-----------------------+
|                    | NCBI Entrez           |
+--------------------+-----------------------+
|                    | HGNC                  |
+--------------------+-----------------------+
|                    | HGMD Public           |
+--------------------+-----------------------+
|                    | ProteinAtlas          |
+--------------------+-----------------------+
|                    | PubMed                |
+--------------------+-----------------------+
|                    | ClinVar               |
+--------------------+-----------------------+
|                    | EnsEMBL               |
+--------------------+-----------------------+
|                    | MetaDome              |
+--------------------+-----------------------+
|                    | PanelApp              |
+--------------------+-----------------------+
|                    | MGI                   |
+--------------------+-----------------------+
| Variant Score/Tool | MutationTaster        |
+--------------------+-----------------------+
|                    | varSEAKSplicing       |
+--------------------+-----------------------+
|                    | UMD Predictor         |
+--------------------+-----------------------+
|                    | PolyPhen 2            |
+--------------------+-----------------------+
|                    | Human Splicing Finder |
+--------------------+-----------------------+
| Variant Database   | Beacon Network        |
+--------------------+-----------------------+
|                    | Varsome               |
+--------------------+-----------------------+
| Genome Browser     | Locus in local IGV    |
+--------------------+-----------------------+
|                    | Public UCSC           |
+--------------------+-----------------------+
|                    | DGV                   |
+--------------------+-----------------------+
|                    | EnsEMBL               |
+--------------------+-----------------------+
|                    | gnomAD                |
+--------------------+-----------------------+

---------------------------------------
Adding and Updating Databases and Tools
---------------------------------------

We invite users to contribute to VarFish databases and tools (of course also VarFish itself) through our project and GitHub issue tracker at https://github.com/varfish-org/varfish-server or by emailing us directly.
In this section, we summarise the process of extending the databases and tool selection.
However, as this a very large topic, we suggest users contact us with their suggestions by email or through the GitHub issue tracker to get more information.
We will also be happy to work with users in finding the best way of integrating new tools and database.

Link-Outs Modifications
=======================

Adding a new tool or database by adding a link from a variant or gene is usually very simple.
However, it requires that the database is accessible through the web (or can be controlled by hyperlinks as is the case with IGV).
Further, it must be possible to create "deep links" into the database or tool.
For example, it is possible to directly create a link to a position into the UCSC genome browser linke this.

::

    https://genome-euro.ucsc.edu/cgi-bin/hgTracks?db=hg19&position=21:11038733-11038733

However, tools such as VariantValidator do not allow this but an API must be used.
There are some databases and tools where it is not possible to created deep links and the database or tool author would have to create this functionality first.

Database Modifications
======================

Updating databases is more complicated.
Overall, the steps are as follows:

- The data must be downloaded and converted into TSV (tab-separated values) file(s).
  For this, we are maintaining a Snakemake workflow on GitHub at https://github.com/varfish-org/varfish-db-downloader.
- The VarFish source code must be modified to

    - create a new Django model class to manage the database table(s) for the new database,
    - create importer code for loading the data into the database,
    - adjust the code for the user interface to display the data (or use it in a different fashion),
    - (potentially) adjust the query generation code to incorporate the new database in the queries,

   Also, the documentation has to be adjusted.

We strongly recommend users to contact us for getting support with this.
