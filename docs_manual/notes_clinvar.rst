.. _notes_clinvar:

=============
ClinVar Notes
=============

This section contains notes regarding ClinVar and its integration into VarFish.
It outlines issues with the interpretation of variants as well as their resolution in VarFish and the rationale for the taken decisions.

ClinVar entries have two major labels:

variant assertion
    The assertion about the pathogenicity of a variant, e.g., *likely benign* or *pathogenic*.
review status
    A grading of how well a variant is reviewed.
    This is shown as a star rating on the ClinVar website.

Some reference ClinVar records (RVC identifiers) refer to one submission (SCV identifiers).
Multiple reference ClinVar records are summarised in variant ClinVar records (VCV identifiers).

----------------------------
Review Status Interpretation
----------------------------

The interpretation of the status of a ClinVar record can be challenging.
This is caused by two points.

Overall, there are the following occurences in ClinVar of clinvar assertion (June 4, 2020).
Note that some only make sense together with the others (e.g., "no conflicts" only makes sense if there is more than one submission).

======== ================================
 Count   ClinVar Status
======== ================================
  12,342 conflicting interpretations
 839,966 criteria provided
  55,467 multiple submitters
  71,858 no assertion criteria provided
  17,068 no assertion provided
  55,467 no conflicts
   5,751 practice guideline
  11,172 reviewed by expert panel
 772,157 single submitter
======== ================================

**In ClinVar** the star ratings are assigned as follows

=====  ===========================================================
Stars  Description
=====  ===========================================================
none   no assertion criteria provided **OR**
       single submitter, no assertion provided
one    single submitter, criteria provided **OR**
       criteria provided &
       multiple submitters, conflicting interpretations
two    criteria provided, multiple submitters, no conflicts
three  reviewed by expert panel
four   practice guideline
=====  ===========================================================

In particular, the missing distinction between "no assertion criteria provided" and "no assertion provided" is misleading.
Also, it can be misleading that records with an assertion criteria override those without.
In several records, good literature has been curated without an assertion criteria while many records from clinical testing companies have an assertion criteria but no phenotype and less diligence has been made as with good research.

==========================
Merging of ClinVar Records
==========================

The algorithm for merging multiple records in ClinVar to display the VCV records is not public.
Also, given the issues with ClinVar's star rating from above, VarFish uses a modified display from ClinVar's.
Instead of ClinVar's gold stars, VarFish assigns points.

========  ==================================================
 Points    Condition
========  ==================================================
none      origin is somatic **OR** no assertion provided
one       single submitter **OR**
          multiple submitters, conflicting interpretations
two       multiple submitters, no conflicting interpretation
three     reviewed by expert panel **OR**
          practice guideline
========  ==================================================

Importantly, Varfish will still display all ClinVar records in the variant display and link out to ClinVar so the user can make their own assessment.
The role of ClinVar in VarFish is to assist the user in quickly find variants present in ClinVar and not to override the user in any way.

The rationale:

- ClinVar entries for somatic variants and those without a variant assessment are of little interest.
- Multiple submitters are better than one submitter, regardless of the assertion criteria.
  Requiring assertion criteria or expert panel status is good for ClinVar to foster submission of assertion criteria or applications for expert panels but less important for VarFish users.
- Variants for practice guideline are less important for VarFish's use case.
  Thus, collapsing them with "reviewed by expert panel" should not make a problem.

VarFish merges ClinVar records based on the following algorithm.

0. Generally, *benign* and *likely benign* is merged to *likely benign/benign*, same for *pathogenic* and *likely pathogenic*.
   Records with *uncertain significance* are ignored in merging if there is at least one *(likely) benign/pathogenic* assessment.
1. Records flagged with *practice guideline* or *expert panel* will be assigned three points and override any other assessment.
   Within three point variants, practice guideline beat expert panel.
2. In the case that there is only one record, that record's assessment is used.
   Note that this will include RCV records in ClinVar that are already merged.
   Assign one point.
3. In the case of two or more records:

    - Ignore *uncertain significance* records as outlined in (0).
    - If there are conflicting interpretations, mark the record as such.
    - Otherwise, merge *likely* and non-*likely* assertions and add *no conflicting interpretation* if more than one non-*uncertain significance* record.
    - Assign one point in case of conflicts and two points in case of consistency.

Further, each variant is annotated with an ACMG-style rating.
In the case of having an "likely X/X" assertion, ACMG:1.5 or ACMG:4.5 is assigned.
In the case of conflicting assertions, an ACMG score of 3 is assigned but the variant is flagged with a "C" to indicate conflicting interpretations.
Note that uncertain vs. benign does not create a conflict as well as uncertain vs. pathogenic.

========
Examples
========

1. INPUT
    - practice guideline, likely pathogenic
    - reviewed by expert panel, likely pathogenic
    - single submitter, pathogenic
   OUTPUT
    - reviewed by expert panel, likely pathogenic
    - three points; ACMG:4-LP
2. INPUT
    - single submitter, pathogenic
    - multiple submitters, no conflict, likely pathogenic
   OUTPUT
    - multiple submitters, no conflict, likely pathogenic/pathogenic
    - two points; ACMG:4.5-LP-P
3. INPUT
    - single submitter, pathogenic
    - single submitter, uncertain significance
    - single submitter, likely pathogenic
   OUTPUT
    - multiple submitters, no conflict, likely pathogenic/pathogenic
    - two points; ACMG:4.5-LP-P
4. INPUT
    - single submitter, pathogenic
    - multiple submitters, uncertain significance
   OUTPUT
    - single submitter, likely pathogenic
    - one point; ACMG:4-LP
5. INPUT
    - single submitter, pathogenic
    - multiple single submitters, likely benign
   OUTPUT
    - multiple submitters, conflicting interpretations, uncertain significance
    - one point; ACMG:3
