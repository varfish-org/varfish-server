.. _sop_supporting:

===============
Supporting SOPs
===============

This appendix contains :term:`SOPs<SOP>` that do not directly deal with variant filtration but are supportive in the the workflow of causative variant identification in mendelian diseases from high-throughput sequencing data.

.. contents:: Contents
    :local:
    :depth: 1

.. raw:: latex

    \cleartoleftpage

.. _sop_quality_control:

--------------------
SOP: Quality Control
--------------------

Aims and Scope
==============

This :term:`SOP` explains how to use VarFish to get a gauge of the quality of the exome at hand.
For this, VarFish provides technical metrics such as exon depth of coverage and metrics that allow inference about the donor and thus allow to detect sample swaps.

Result
======

The result of this step is to indicate whether the sequencing results can be trusted in terms of consistency with pedigree and sex meta data and in terms of quality (depth of coverage and percentage of duplicated reads).

Steps
=====

Consider the section "Alignment Quality Control".

1. The table "Target Coverage" indicates the percentage of targets in each sample that has coverage of at least 10x, 20x, etc.
   The detection of het. variants below 10x is not reliable, 20x or more is recommended.
   However, also note that if an target has a coverage of above 10x in all but one position that falls to 9x, the target counts as not having at least 10x coverage.
   The thresholds from below have worked well for the authors using recent technologies.

2. The table "Stats" gives some overall sequencing metrics.
   The values of "Duplicates".
   The values of "Pairs”, "Average Insert Sizes”, and "SD Insert Size” are mostly of informative value.
   They are useful for detecting outliers in the context of multiple samples of the same study.

Consider the Figures in :term:`QC` Plots

1. The plot "Relatedness vs. IBS0” is only informative for families.
   The relatedness coefficient (RC) should be around 1.0 for parent-child relations, 0.5 for siblings and decreases further with lower relatedness.
   The IBS0 value is around 0.0 for parent-child relations and increases with lower relatedness.
   The RC between monozygotic twins and technical replicates of same sample is expected to be around 2.0.
   Parent-child relations and sibling-sibling relations should be in the top left of the plot.
   Unless the parents are consanguineous, they should be in the lower-right corner of the plot.
   Unexpected RC counts indicate possible sample swaps or discordance between the samples’ genetics and the pedigree from the meta data.

2. The plot "Rate of het. calls on chrX” allows inference of the genetic sex of the sample.
   This ration is expected to be well below 0.5 for male individuals and well above 0.5 (actually around 1.0-2.0) for female individuals.
   Unexpected ratios indicate a sample swap and the corresponding points will be indicated in red color.

In the case of unexpected relatedness, samples must be checked for sample swap.
Unexpected inferred sex can be caused by incorrect meta data (e.g., for fetuses) and can also help resolve cases of unexpected relationships (e.g., child/parent swaps).
Samples with technical quality metrics violating thresholds are candidates for being repeated.

.. raw:: latex

    \clearpage

Thresholds
==========

Thresholds of course always depend on overall sequencing depth and technology.
Based on our experience with recent technologies (Agilent SureSelect Human All Exome V6 on Illumina NextSeq 500 or HiSeq 4000 machines in 2018/2019) we propose the following thresholds. We recommend to adjust them in your setting depending on technology and previous experience.

==============  ==============  =====================  =======================
    Metric       Good / Green    Acceptable / Yellow    Below Standards / Red
==============  ==============  =====================  =======================
 10x coverage    ≥ 98%           ≥ 95%                  < 95%
 20x coverage    ≥ 98%           ≥ 95%                  < 95%
 Duplicates      ≤ 10%           ≤ 20%                  > 20%
==============  ==============  =====================  =======================

.. raw:: latex

    \cleartoleftpage

.. _sop_database_literature_research:

-----------------------------------
SOP: Database & Literature Research
-----------------------------------

Aims and Scope
==============

The aim of this section is to highlight the most important databases that are either integrated into VarFish or that VarFish links out to.
The list is not comprehensive and we refer the reader to the ACMG guidelines

Result
======

Steps
=====


.. raw:: latex

    \cleartoleftpage

.. _sop_pathogenicity_score_interpretation:

--------------------------------------
SOP: Pathogencity Score Interpretation
--------------------------------------

Aims and Scope
==============

The aim of this section is to provide guidelines in the interpretation of variant pathogenicity scores.
Please refer to the original scoring methods' publications for authorative information.

Result
======

For each scored variant, an understanding of how likely a variant has a pathogenic biomedical effect.

Steps
=====

1. VarFish uses the PHRED-scaled :term:`CADD` score, the :term:`CADD` authors `recommend a cutoff of 15 ("somewhere betwen 10 and 20, maybe 15") <https://cadd.gs.washington.edu/info>`_.
   As a frame of reference: a CADD score of 10 translates into the top 10% of CADD-scored SNVs, 15 to the top 3.1%, 20, to the top 1%, 30 to the top 0.1%.

2. :term:`MutationTaster` provides a classification into `one of four possible types <http://www.mutationtaster.org/info/documentation.html>`_:
   *disease causing automatic* - known to be disease causing, *polymorphism automatic* - known to be benign, *disease causing* - predicted to be deleterious, *polymorphism* - predicted to be benign.
   Additionally, a probability for the prediction's correctness by a Bayes classifier is given.
   The variants annotated with *automatic* can be generally trusted.
   The other predictions' reliability can be gauged by the Bayes classifier probability.
   The probabilities themselves are difficult to interpret, they are best set into relation to each other.

3. :term:`UMD Predictor` can only be used for scoring :term:`SNVs<SNV>`.
   The scores range from 0 to 100 and the authors give the following thresholds `in their original publication <https://onlinelibrary.wiley.com/doi/full/10.1002/humu.22965>`_:
   *"(i) <50 polymorphism; (ii) 50–64 probable polymorphism; (iii) 65–74 probably pathogenic mutation; and (iv) >74 pathogenic mutation."*

Thresholds
==========

The following thresholds/grading of variants can be used for grading pathogenicity scores.
Note that pathogenicity scores are extremely useful for sorting/ranking variants in the prioritization step.
However, any cutoff and assignment of a pathogenicity will have false positives and false negatives.

+----------------+--------+-----------------+-------------------+------------+
| score          | benign |  likely benign  | likely pathogenic | pathogenic |
+================+========+=================+===================+============+
| CADD           | <10    | ≥10, <15        | ≥15, <20          | ≥20        |
+----------------+--------+-----------------+-------------------+------------+
| MutationTaster | polymorphims (automatic) | disease causing (automatic)    |
+----------------+--------------------------+-------------------+------------+
| UMD Predictor  | <50     ≥50, <65         | ≥65, <75          | ≥75        |
+----------------+--------------------------+-------------------+------------+


.. raw:: latex

    \cleartoleftpage

.. _sop_phenotype_score_interpretation:

-----------------------------------
SOP: Phenotype Score Interpretation
-----------------------------------

Aims and Scope
==============

The aim of this section is to provide guidelines in the interpretation of phenotype match scores.
Please refer to the original scoring methods' publications for authorative information.

Result
======

For each scored set of genes, an understanding of the individual scores.

Steps
=====

Generally, the phenotype scores are computed for each gene and compare the phenotypes given for the affected individual and the phenotypes linked to the gene.
Thus, they depend on a good clinical annotation of the case and the curation of the gene-to-phenotype database.
VarFish uses the :term:`Exomiser` software for implementing the :term:`Phenix`, :term:`Phive`, and :term:`HiPhive` scores.

1. The :term:`Phenix` score is built from phenotypes of known human disease genes based on a concept called *information content*.
   Thus, only already known disease genes will obtain a non-zero score.

   An important caveat is that :term:`Phenix` will normalize the scores with respect to the genes from the filtered variant list.
   Thus, a change in filter parameters and subsequently in the list of genes in the query will change the score of a given gene.

2. The :term:`Phive` score also incorporates mouse phenotypes by linking human and mouse physiology and homologous genes.
   Thus, it can be used to find new disease genes in human if the gene's mouse homologue has a proper phenotype annotation.

   TODO: also normalized relatively?

3. The :term:`HiPhive` score extends the :term:`Phive` idea with zebrafish and protein-protein interaction networks.
   It is the most powerful of the Phenix/Phive/HiPhive family in that new disease genes can be identified from mouse, fish, and also by a link via protein interactions.
   However, it also allows for relatively indirect links that might be more complex to followup and proof the etiology.

   TODO: also normalized relatively?

Overall, the phenotype prioritization scores are extremely useful for ranking genes by matches to the clinical phenotype annotation of the individual.
However, they cannot be interpreted meaningfully on their own and are only meaningful when compared for the same list of genes.
