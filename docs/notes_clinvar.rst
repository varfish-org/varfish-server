.. _notes_clinvar:

=============
ClinVar Notes
=============

This section contains notes regarding ClinVar and its integration into VarFish.

ClinVar Annotation Modes
-------------------------

Starting with VarFish ``v1.2.2`` and data version ``20210728c``, VarFish provides two different annotation modes.
These differ in how they require assessment criteria in the aggregation.

Normal ClinVar Mode
    Records are merged as in ClinVar.
    That is, "practice guideline" is preferred over all others.
    Then, "reviewed by expert panel" takes precedence.
    In all other cases, if there are submissions with assessment criteria then only these are interpreted.

"Paranoid" Mode
    In this mode, submissions with and without assessment criteria are considered to be on one level.
    This results in capturing more interpretations per variant.

When using "Normal ClinVar Mode" annotation, you should get the same aggregated summary as in ClinVar VCV records.
The only source of differences should be that the local VarFish version will be outdated when compared to ClinVar.

In "Paranoid Mode" annotation you will get many more conflicts and pathogenic variants because the submissions without assessment criteria are sometimes of lower quality and generate noise.

**Important:** As of the current version, VarFish **always uses "Paranoid Mode"** for filtering operations.
This ensures maximum sensitivity in detecting potentially pathogenic variants by considering all available interpretations,
including those without formal assessment criteria.

Filtering by ClinVar Interpretations
-------------------------------------

VarFish uses the "Paranoid Mode" annotation for all ClinVar filtering operations. This means:

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
    The legacy ``clinvar_paranoid_mode`` field in query settings is still accepted for backward compatibility but is ignored, 
    as paranoid mode is now always active. This ensures older saved queries continue to work without modification.

