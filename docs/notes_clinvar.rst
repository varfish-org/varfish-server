.. _notes_clinvar:

=============
ClinVar Notes
=============

This section contains notes regarding ClinVar and its integration into VarFish.

ClinVar Annotation Strategy
---------------------------

VarFish uses a comprehensive annotation strategy that considers all available interpretations for maximum sensitivity.

**Annotation Approach:**
    VarFish aggregates ClinVar submissions by treating those with and without assessment criteria on the same level.
    This captures more interpretations per variant compared to ClinVar's standard aggregation method.
    While this may result in more conflicts, it ensures that potentially pathogenic variants are not missed
    due to lower-quality submissions being excluded.

Filtering by ClinVar Interpretations
-------------------------------------

VarFish considers all available ClinVar interpretations when filtering. This means:

**Multi-Interpretation Handling:**
    Variants may have multiple interpretations listed (e.g., a variant might be classified as both "pathogenic" and "benign" by different submitters).
    When you select specific interpretations (e.g., "pathogenic"), any variant containing those interpretations in its list will be shown.
    
    For example, if you select "pathogenic", you will see:
    
    - Variants with only "pathogenic" classification
    - Variants with conflicting interpretations that include "pathogenic" (e.g., ["pathogenic", "benign"])

**Conflicting Interpretations:**
    A variant is considered to have truly "conflicting" interpretations when it has classifications from different pathogenicity groups:
    
    - **Pathogenic group:** "pathogenic", "likely pathogenic"
    - **Uncertain group:** "uncertain significance"
    - **Benign group:** "benign", "likely benign"
    
    True conflicts occur when interpretations span at least two of these groups (e.g., both "pathogenic" and "benign", 
    or "likely pathogenic" and "uncertain significance").

**Exclude Conflicting Variants Filter:**
    A checkbox option allows you to exclude variants with conflicting interpretations from your results.
    When enabled, only variants with consistent interpretations (from a single pathogenicity group) are displayed.
    This is useful when you want to focus on variants with clear, non-conflicting evidence.

**Visual Indicators:**
    In the results table, variants with conflicting ClinVar interpretations are marked with:
    
    - A warning icon (⚠️) badge indicating the presence of conflicting interpretations
    - Individual badges for each interpretation present in the variant
    - A star rating showing the review status quality
    - A link-out icon to view the full variant details in NCBI ClinVar

**Backward Compatibility:**
    The legacy ``paranoid`` mode in query settings is still accepted for backward compatibility but is ignored.
    This ensures older saved queries continue to work without modification.

