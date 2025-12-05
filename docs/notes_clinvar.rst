.. _notes_clinvar:

=============
ClinVar Notes
=============

This section contains notes regarding ClinVar and its integration into VarFish.
Starting with VarFish ``v1.2.2`` and data version ``20210728c``, VarFish provides two different annotation modes.
These differ in how they require assessment criteria in the aggregation.

Normal ClinVar Mode (default)
    Records are merged as in ClinVar.
    That is, "practice guideline" is preferred over all others.
    Then, "reviewed by expert panel" takes precedence.
    In all other cases, if there are submissions with assessment criteria then only these are interpreted.

"Paranoid" Mode
    In this mode, submissions with and without assessment criteria are considered to be on one level.

When using "Normal ClinVar Mode", you should get the same aggregated summary as in ClinVar VCV records.
The only source of differences should be that the local VarFish version will be outdated when compared to ClinVar.

In "Paranoid Mode" you will get many more conflicts and pathogenic variants because the submissions without assessment criteria are sometimes of lower quality and generate noise.

Filtering by ClinVar Interpretations
-------------------------------------

When filtering variants by ClinVar interpretations, the behavior differs between Normal and Paranoid modes:

**Normal ClinVar Mode:**
    Variants have a single aggregated interpretation (e.g., "pathogenic", "benign", or "conflicting").
    When you select specific interpretations (e.g., "pathogenic"), only variants with that exact interpretation are shown.
    Variants marked as "conflicting" are only shown when the "conflicting interpretations" checkbox is selected.

**Paranoid Mode:**
    Variants may have multiple interpretations listed (e.g., a variant might be classified as both "pathogenic" and "benign" by different submitters).
    When you select specific interpretations, any variant containing those interpretations in its list will be shown.
    For example, if you select "pathogenic", you will see:
    
    - Variants with only "pathogenic" classification
    - Variants with conflicting interpretations that include "pathogenic" (e.g., ["pathogenic", "benign"])
    
    The "conflicting interpretations" checkbox in Paranoid mode will show variants with multiple different interpretations, 
    but becomes redundant if other specific interpretations are already selected, as those will already include the relevant conflicting variants.

