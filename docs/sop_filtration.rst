.. _sop_filtration:

=======================
Variant Filtration SOPs
=======================

This chapter contains :term:`SOPs<SOP>` directly related to the filtration, prioritization, and interpretation of variants.
The first :term:`SOPs<SOP>` cover the filtration of variants for singleton and trio exomes in various modes of inheritance.
When dealing with different case structures (e.g., siblings or only having one parent present), they can be handled with adjusted trio :term:`SOPs<SOP>`.
This is followed with :term:`SOPs<SOP>` for assessing variants for pathogenicity and suitability as candidate variants.

.. contents:: Contents
    :local:
    :depth: 1

.. raw:: latex

    \cleartoleftpage

.. _sop_filter_singleton_autosomal:

------------------------------------------------
SOP: Filtering Singletons for Autosomal Variants
------------------------------------------------

Aims and Scope
==============

The aim of this :term:`SOP` is the filtration of singleton data for variants on the autosomal chromosomes.
Depending on the hypothesis on the mode of inheritance the steps differ slightly.
Alternative actions are given for *de novo*, dominant, homozygous recessive, and compound recessive variants.

Filtration for variants on the X chromosomes is described in :ref:`sop_filter_singleton_xchromosomal`.
The evaluation of variants is described in :ref:`sop_variant_assessment`, the use of phenotype and pathogenicity scores is described in :ref:`sop_prioritization_scores`.

Result
======

The result is a list of variants in compatible mode of inheritance with appropriate population frequency.
These can then be assessed as described in :ref:`sop_variant_assessment`.
A typical WES data set yields the following variant counts (numbers will vary depending on the enrichment kit):

=========  ========  =========  ==========
*de novo*  dominant  hom. rec.  comp. rec.
=========  ========  =========  ==========
0-80       100-500   0-30       TODO
=========  ========  =========  ==========

Steps
=====

#. Use the :guilabel:`Load Preset` button to load filter presets (according to the table below and your mode of inheritance).
#. Configure the :guilabel:`Genotype` according to the table below.

    =========  ===================  ==================  =====================  =====================
    setting    *de novo*            dominant            hom. rec.              comp. rec.
    =========  ===================  ==================  =====================  =====================
    presets    :guilabel:`De Novo`  :guilabel:`Strict`  :guilabel:`Recessive`  :guilabel:`Recessive`
    genotype   0/1                  0/1                 1/1                    c/h index
    =========  ===================  ==================  =====================  =====================

    - For compound recessive mode of inheritance, selecting "c/h index" as mode of inheritance for the child enables the comp. het. mode.


#. Click :guilabel:`Filter & Display`.
#. Compare the resulting variant count with the numbers from the table above.
   Also check that all query result records are displayed\ [#rowlimit]_.
#. Handle unexpected high and low number of variants.

    - In case of too few variants try relaxing the :guilabel:`Quality` settings, *e.g.*, by setting :guilabel:`DP het.` to 8 and :guilabel:`min AAB` to 0.2.
    - Try adjusting the :guilabel:`Frequency` settings (keep in mind incidence rates of the case's disorder).
    - The presets :guilabel:`Relaxed` and :guilabel:`Super Strict` can be used for non-recessive modes of inheritance to adjust multiple thresholds at once.

.. [#rowlimit] Check the :guilabel:`First N of M records` label on above the results table, potentially adjust the :guilabel:`Result row limit` setting you can find in the :menuselection:`More ... --> Miscellaneous` tab.

Thresholds
==========

.. raw:: latex

    \cleartoleftpage

.. _sop_filter_singleton_xchromosomal:

----------------------------------------------------
SOP: Filtering Singletons for X-chromosomal Variants
----------------------------------------------------

Aims and Scope
==============

The aim of this :term:`SOP` is the filtration of singleton data for variants on the X chromosome.
Depending on the hypothesis on the mode of inheritance the steps differ slightly.
Alternative actions are given for *de novo*, dominant, homozygous recessive, and compound recessive variants.

Filtration for variants on the autosomes is described in :ref:`sop_filter_singleton_autosomal`.
The evaluation of variants is described in :ref:`sop_variant_assessment`, the use of phenotype and pathogenicity scores is described in :ref:`sop_prioritization_scores`.

Result
======

The result is a list of variants in compatible mode of inheritance with appropriate population frequency.
These can then be assessed as described in :ref:`sop_variant_assessment`.
A typical WES data set yields the following variant counts (numbers will vary depending on the enrichment kit):

===========  ==========  ===========   ============
X *de novo*  X dominant  X hom. rec.   X comp. rec.
===========  ==========  ===========   ============
TODO         TODO        TODO          TODO
===========  ==========  ===========   ============

Steps
=====

.. note:: The following needs work by a geneticists, also in terms of practicability

#. Use the :guilabel:`Load Preset` button to load filter presets (according to the table below and your mode of inheritance).
#. Configure the :guilabel:`Genotype` according to the table below.

    ============  ===================  ==================  =====================  =====================
    setting       X *de novo*          X dominant          X hom. rec.            X comp. rec.
    ============  ===================  ==================  =====================  =====================
    presets       :guilabel:`De Novo`  :guilabel:`Strict`  :guilabel:`Recessive`  :guilabel:`Recessive`
    genotype (M)  1/1                  1/1                 N/A                    N/A
    genotype (F)  0/1                  0/1                 1/1                    c/h index
    ============  ===================  ==================  =====================  =====================

    - The genotype of the index is chosen based on its sex (male M, female F).
    - For compound recessive mode of inheritance, selecting "c/h index" as mode of inheritance for the daughter.

#. Enter ``chrX`` into the field :menuselection:`Gene Lists & Regions --> Genomic Region`.

#. Click :guilabel:`Filter & Display`.

#. Compare the resulting variant count with the numbers from the table above.
   Also check that all query result records are displayed\ [#rowlimit]_.

#. Handle unexpected high and low number of variants.

    - In case of too few variants try relaxing the :guilabel:`Quality` settings, *e.g.*, by setting :guilabel:`DP het.` to 8 and :guilabel:`min AAB` to 0.2.
    - Try adjusting the :guilabel:`Frequency` settings (keep in mind incidence rates of the case's disorder).
    - The presets :guilabel:`Relaxed` and :guilabel:`Super Strict` can be used for non-recessive modes of inheritance to adjust multiple thresholds at once.

Thresholds
==========

.. raw:: latex

    \cleartoleftpage

.. _sop_filter_trio_autosomal:

-------------------------------------------
SOP: Filtering Trios for Autosomal Variants
-------------------------------------------

Aims and Scope
==============

The aim of this :term:`SOP` is the filtration of trio data for variants on the autosomal chromosomes.
Depending on the hypothesis on the mode of inheritance the steps differ slightly.
Alternative actions are given for *de novo*, dominant, homozygous recessive, and compound recessive variants.

Filtration for variants on the X chromosomes is described in :ref:`sop_filter_trio_xchromosomal`.
The evaluation of variants is described in :ref:`sop_variant_assessment`, the use of phenotype and pathogenicity scores is described in :ref:`sop_prioritization_scores`.

Result
======

The result is a list of variants in compatible mode of inheritance with appropriate population frequency.
These can then be assessed as described in :ref:`sop_variant_assessment`.
A typical WES data set yields the following variant counts (numbers will vary depending on the enrichment kit):

=========  ========  =========  ==========
de novo    dominant  hom. rec.  comp. rec.
=========  ========  =========  ==========
0-3        50-150    2-75       2-20
=========  ========  =========  ==========

Steps
=====

#. Use the :guilabel:`Load Preset` button to load filter presets (according to the table below and your mode of inheritance).
#. Configure the :guilabel:`Genotype` according to the table below.

    =========  ==================  ==================  =====================  =====================
    setting    *de novo*           dominant            hom. rec.              comp. rec.
    =========  ==================  ==================  =====================  =====================
    presets    :guilabel:`Strict`  :guilabel:`Strict`  :guilabel:`Recessive`  :guilabel:`Recessive`
    genotype
    index      0/1                 0/1                 1/1                    c/h index
    parents    0/0, 0/0            0/0, 0/1            0/1, 0/1               --
    =========  ==================  ==================  =====================  =====================

    - For dominant mode of inheritance, set the genotypes of the affected parent to 0/1 and the unaffected parent to 0/0.
    - For compound recessive mode of inheritance, selecting "c/h index" as mode of inheritance for the child enables the comp. het. mode and the parents' genotype does have to be selected.

#. Click :guilabel:`Filter & Display`.
#. Compare the resulting variant count with the numbers from the table above.
   Also check that all query result records\ [#rowlimit]_.
#. Handle unexpected high and low number of variants.

    - Too many *de novo* and too few variants in the other modes of inheritance can be an indicator of issues with the sample relatedness (cf. :ref:`sop_quality_control`).
    - In case of too few variants try relaxing the :guilabel:`Quality` settings, *e.g.*, by setting :guilabel:`DP het.` to 8 and :guilabel:`min AAB` to 0.2.
      In the case of too few *de novo* variants, try setting the :guilabel:`max AD` setting of the parents to 2.
    - Try adjusting the :guilabel:`Frequency` settings (keep in mind incidence rates of the case's disorder).
    - The presets :guilabel:`Relaxed` and :guilabel:`Super Strict` can be used for non-recessive modes of inheritance to adjust multiple thresholds at once.

Thresholds
==========

TODO

.. raw:: latex

    \cleartoleftpage

.. _sop_filter_trio_xchromosomal:

-----------------------------------------------
SOP: Filtering Trios for X-chromosomal variants
-----------------------------------------------

Aims and Scope
==============

The aim of this :term:`SOP` is the filtration of trio data for variants on the X chromosome.
Depending on the hypothesis on the mode of inheritance the steps differ slightly.
Alternative actions are given for X-linked *de novo*, dominant, recessive.

Filtration for variants on the autosomes is described in :ref:`sop_filter_trio_autosomal`.
The evaluation of variants is described in :ref:`sop_variant_assessment`, the use of phenotype and pathogenicity scores is described in :ref:`sop_prioritization_scores`.

Result
======

The result is a list of variants in compatible mode of inheritance with appropriate population frequency.
These can then be assessed as described in :ref:`sop_variant_assessment`.
A typical WES data set yields the following variant counts (numbers will vary depending on the enrichment kit):

===========  ==========  ===========   ============
X *de novo*  X dominant  X hom. rec.   X comp. rec.
===========  ==========  ===========   ============
TODO         TODO        TODO          TODO
===========  ==========  ===========   ============

Steps
=====

.. note:: The following needs work by a geneticists, also in terms of practicability

#. Use the :guilabel:`Load Preset` button to load filter presets (according to the table below and your mode of inheritance).
#. Configure the :guilabel:`Genotype` according to the table below.

    =========  ==================  ==================  =====================  =====================
    setting    X *de novo*         X dominant          X hom. rec.            X comp. rec.
    =========  ==================  ==================  =====================  =====================
    presets    :guilabel:`Strict`  :guilabel:`Strict`  :guilabel:`Recessive`  :guilabel:`Recessive`
    genotype
    index (M)  1/1                 1/1                 N/A                    c/h index
    index (F)  0/1                 0/1                 1/1                    c/h index
    mother     0/0                 0/1 or 0/0          0/1                    --
    father     0/0                 1/1 or 0/0          1/1                    --
    =========  ==================  ==================  =====================  =====================

    - The genotype of the index is chosen based on its sex (male M, female F).
    - For dominant mode of inheritance, set the genotypes of the affected parent to variant (0/1 or 1/1 according to the table) and of the unaffected to 0/0.
    - For compound recessive mode of inheritance, selecting "c/h index" as mode of inheritance for the child enables the comp. het. mode and the parents' genotype does have to be selected.
#. Enter ``chrX`` into the field :menuselection:`Gene Lists & Regions --> Genomic Region`.

#. Click :guilabel:`Filter & Display`.
#. Compare the resulting variant count with the numbers from the table above.
   Also check that all query result records are displayed (check the :guilabel:`First N of M records` label on above the results table, potentially adjust the :guilabel:`Result row limit` setting you can find in the :menuselection:`More ... --> Miscellaneous` tab).
#. Handle unexpected high and low number of variants.

    - Too many *de novo* and too few variants in the other modes of inheritance can be an indicator of issues with the sample relatedness (cf. :ref:`sop_quality_control`).
    - In case of too few variants try relaxing the :guilabel:`Quality` settings, *e.g.*, by setting :guilabel:`DP het.` to 8 and :guilabel:`min AAB` to 0.2.
      In the case of too few *de novo* variants, try setting the :guilabel:`max AD` setting of the parents to 2.
    - Try adjusting the :guilabel:`Frequency` settings (keep in mind incidence rates of the case's disorder).
    - The presets :guilabel:`Relaxed` and :guilabel:`Super Strict` can be used for non-recessive modes of inheritance to adjust multiple thresholds at once.

Thresholds
==========

.. raw:: latex

    \cleartoleftpage

.. _sop_prioritization_scores:

-----------------------------------------------------------
SOP: Prioritization with Phenotype and Pathogenicity Scores
-----------------------------------------------------------

Aims and Scope
==============

The aim of this :term:`SOP` is to use scores for prioritizing a list of candidate variants.
Phenotype scores can be used for ranking variants by their affected gene's match to the patient's phenotypes.
Pathogenicity scores can be used for estimating the impact of a variant.

The filtration of variants is described in the :term:`SOPs<SOP>` above.
For guidelines on interpreting the scores see :ref:`sop_phenotype_score_interpretation` and :ref:`sop_pathogenicity_score_interpretation`.

Result
======

The result is a list of variants annotated with phenotype and/or pathogenicity scores that can be used for sorting and ranking variants.
Further, by putting thresholds on the largest rank to consider or thresholds on the scores, the list of variants to be assessed can be shortened.

Steps
=====

#. Open the :menuselection:`More ... --> Prioritization` tab.

#. For using phenotype-based prioritization

    - tick the :guilabel:`Enable phenotype-based prioritization` box,
    - select an appropriate prioritization :guilabel:`Algorithms`, and
    - enter (or paste) the HPO terms into the :guilabel:`HPO Terms` field.

#. For using variant pathogenicity prioritization

    - tick the :guilabel:`Enable variant pathogenicity-based prioritization` box, and
    - select the scoring method\ [#umd]_ to use.

#. Click :guilabel:`Filter & Display` to trigger the filtration.

    - Also check that all query result records are displayed\ [#rowlimit]_.
      The limit is applied to the variants sent for prioritization.
      *You will not see the N top-ranking records but you will see a ranking of an arbitrary selection of N records in the case that the limit of records to display is smaller than the query result size N*.

#. Click on the :guilabel:`score` and :guilabel:`rank` heading below the :guilabel:`phenotype`, :guilabel:`pathogenicity`, and/or :guilabel:`pheno. & patho.` columns to sort the table by phenotype, pathogenicity, or a combination of both scores.

#. Consider the top variants by one of the sorting methods from above, stop based on the rank or score:

    - Rank: *Consider the top N (e.g., =20) variants only.*

        - If you are in a time-limited setting, you should pick the number N in advance of your study to get reproducible results in terms of diagnostic yield.

    - Score: (Note that the distribution of the different scores varies significantly).

        - *Consider the top-scoring variants until the score drops by a factor of 2 from one variant to the next*.
        - *Consider the top-scoring variants until the score drops below a threshold T*.

See :ref:`sop_phenotype_score_interpretation` and :ref:`sop_pathogenicity_score_interpretation` for more information in score interpretation.

.. [#umd] For using the :term:`UMD Predictor` score you have to obtain a API token from https://umd-predictor.eu/ and enter it in VarFish in your user profile.
   You can reach the user profile by clicking on the person icon on the top left, then :menuselection:`User Profile --> Settings --> Update --> UMD Predictor API Token`.
   Note that UMD Predictor can only score :term:`SNVs<SNV>`.

Thresholds
==========

.. raw:: latex

    \cleartoleftpage

.. _sop_variant_assessment:

-----------------------
SOP: Variant Assessment
-----------------------

Aims and Scope
==============

This :term:`SOP` describes how to assess variants with the information integrated into VarFish.
Clicking the little ">" on the left of the result table folds out the details of the given variant.

Result
======

The result is a better understanding of the variant and gene.

Steps
=====

.. note:: The following needs refinement. Actually, it does not read like a SOP but rather an extended manual.

#. Consider the :guilabel:`Gene` information box.

    - The :guilabel:`Name`, :guilabel:`Gene Family`, and :guilabel:`NCBI Summary` give a first impression about the gene and its molecular functional and implication in diseases.
      Genes with missing or very short :guilabel:`NCBI Summary` are often not well-characterized and such genes are hard to link to diseases.
    - :guilabel:`ClinVar for Gene` gives the number of pathogenic and likely pathogenic variants in the gene and shows how often the gene has been implicated in disease in :term:`ClinVar`.
    - :guilabel:`HPO Terms` displays all HPO terms associated with a gene and, if present, the annotated modes of inheritance of diseases linked to this gene.
    - :guilabel:`OMIM Phenotypes` gives the OMIM diseases linked to the gene.
    - :guilabel:`Gene RIFs` displays short "reference into function" notes on :term:`PubMed` articles that report on the gene.
    - :guilabel:`Constraints` shows gene contraint scores from ExAc and gnomAD for this gene.
    - The remaining fields provide link-outs into :term:`NCBI` :term:`Entrez`, :term:`ENSEMBL`, and :term:`OMIM`.

#. The :guilabel:`ClinVar for Variant` table shows :term:`ClinVar` annotations for the given variant, if any.

#. The :guilabel:`Frequency Details` table provides detailed information about the frequency of the variant in different populations given in the different population databases.

#. The :guilabel:`Transcript Information` table shows the impact of the variant on all transcripts of the gene.

#. The :guilabel:`Genotype and Call Infos` provides detailed information about the variant call.

#. The :guilabel:`UCSC 100 Vertebrate Conservation` box shows the alignment of the corresponding amino acid in the :term:`UCSC` 100 vertebrate alignment (the evoluationary distance to human decreases from left to right), if available.
   This information can be used for getting a feeling on how conserved the location is in the gene.

.. raw:: latex

    \cleartoleftpage

.. _sop_variant_link_outs:

----------------------------
SOP: Using Variant Link-Outs
----------------------------

Aims and Scope
==============

This :term:`SOP` describes how to use the most relevant link-out features of VarFish for estimating the pathogenicity and relevance of a given variant for a case's disorder.
Note that this is an non-comprehensive list of pragmatic points that fit on two pages of paper.
The :term:`ACMG` and :term:`ACGS` guidlines.

Result
======

The result is a better understanding of the variant's pathogenic potential.

Steps
=====

- Use the :guilabel:`IGV` button on the right of the variant result table row.
  If :term:`IGV` is running and configured properly then IGV will jump to the given position such that you can inspect the variant in the raw data.

- Use the :guilabel:`MT` button on the right of the variant result table row.
  This will run :term:`MutationTaster` (MT) on your variant.
  The result page displays the analysis summary for each affected transcript and then details for each affected transcript.

    - The prediction :guilabel:`disease causing (automatic)` and :guilabel:`polymorphism (automatic)` ist most important, followed by the probability given by the :term:`MT<MutationTaster>` classifier.
    - The :guilabel:`splice sites` analysis gives interesting information about whether splicing is predicted to be affected.
    - The :guilabel:`conservation` provides information about conservation.

The following link-outs are shown when clicking on the little downward arrow next to :guilabel:`IGV`.

- Use :guilabel:`Locus @UCSC` to consider the locus in :term:`UCSC` genome browser.

- Use :guilabel:`Human Splicing Finder` (HSF) for estimating the effect of a variant on the splicing of a gene's transcripts.
  The link-out will open a new tab showing the results of the HSF (which will also give predictions for deepl intronic variants).

- Use :guilabel:`Query varSEAK Splicing` for also estimating the effect of a variant on splicing of a gene's transcripts.
  varSEAK does not show results of deep intronic variants.

- Use :guilabel:`Query PolyPhen 2` for obtaining PolyPhen 2 scores of missense variants.

- Use :guilabel:`Query UMD Predictor`\ [#umd]_ for querying the UMD Predictor (note that this only works for :term:`SNVs<SNV>`.

- Use: :guilabel:`Query Varsome` for looking up the variant in :term:`Varsome`

.. raw:: latex

    \cleartoleftpage

.. _sop_gene_link_outs:

-------------------------
SOP: Using Gene Link-Outs
-------------------------

Aims and Scope
==============

This :term:`SOP` describes how to use the most relevant link-out features of VarFish for estimating the relevance of a given for a case's disorder.
Note that this is a highly non-comprehensive list that only highlights selected aspects of some databases that fits on two pages of paper.

Result
======

The result is a better understanding on whether a defect in the gene can be responsible for the case's disorder.

Steps
=====

.. note:: The following needs to be done.
