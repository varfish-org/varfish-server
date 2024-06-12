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
