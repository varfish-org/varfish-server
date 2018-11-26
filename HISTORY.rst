===================
History / Changelog
===================

-----------------
HEAD (unreleased)
-----------------

The focus of the upcoming release is adding display of variant statistics for cases.

- Gathering the following statistics for each individuals in a case:
    - transition to transversion ratio for on-target variants
- Adding ``var_qc_stats`` module with analysis algorithms similar to (Pedersen and Quinlan, 2017).
- Display statistics results on case detail page.

------
v0.7.0
------

This release has one main feature: it adds support for submitting variants to MutationDistiller.

End-User Summary
================

- Added support for submitting variants to MutationDistiller from the Variant Filtration Form.
- Added "Full Exome" filter preset for including all variants passing genotype filter.
- Greatly speeded up VCF export.

Full Change List
================

- Adding "Full Exome" filter preset.
- Adding support for submitting filtration results to MutationDistiller.
- Pinning redis, cf. https://github.com/celery/celery/issues/5175
- Pinning celery, cf. https://github.com/celery/celery/issues/4878
- Refactoring query building to a mixin-based architecture to make code more reuseable and allow better reusability.
- Adding ``ExportVcfFileFilterQuery`` for faster VCF export.

------
v0.6.3
------

A bugfix release.

End-User Summary
================

- Fixing bug that caused the clinvar report to fail when restoring previous query.

Full Change List
================

- Making sure returning to clinvar report works again.
- Enabling SODAR-core adminalerts app.
- Including authors and changelog in manual.

------
v0.6.2
------

A bugfix release.

End-User Summary
================

- Fixing search bug with upper/lower case normalization.
- Fixed bug with whitelist/blacklist when restoring settings.
- Extended documentation, added screenshots.
- Previous flag state is now properly written to the timeline.

------
v0.6.1
------

End-User Summary
================

- Adding forgotten help link to title bar.

------
v0.6.0
------

End-User Summary
================

- Various smaller bug fixes and user interface improvements.
- Adding summary flag for colouring result lines.
- Allow filtering variants by flags.
- Integrating flags etc. also into downloadable TSV/Excel files.
- Adding new annotation: HGMD public via ENSEMBL.
- Adding comments and flags now appears in the timeline.
- Varfish stores your previous settings automatically and restores them on the next form view.

Full Change List
================

- Allowing Javascript to access CSRF token, enables AJAX in production.
- ``SmallVariant``s are now also identified by the ``ensembl_gene_id``.
  This fixes an annotation error.
- Adding ``flag_summary`` to ``SmallVariantFlags`` for giving an overall summary.
- Extending filtration form to filter by flags.
- Added new app ``hgmd`` for ``HGMD_PUBLIC`` data from ENSEMBL.
- Adding ``make black`` to ``Makefile``.
- Changed default frequencies.
- Improving integration of comments and flags with the timeline app.
- Also properly integrating import of cases etc. with timeline app.
- Added ``SmallVariantQuery`` model and integrated it for automatically storing form queries and restoring them.

------
v0.5.0
------

End-User Summary
================

This is a major upgrade in terms of features and usability.
Please note that this a "dot zero" release, we will fix broken things in a timely manner.

Major changes include:

- The "AD" form field was split into one for het. and one for hom. variants.
- Clinvar entries are now properly displayed.
- Enabling filtering for clinvar membership and pathogenicity.
- Fixing file export.
- Allowing to mark variants with flags and add comments to them.
- Adding clinvar-centric report.
- Filtration now also works for pedigrees containing samples without genotypes.
- Adding functionality to search for samples.

Full Change List
================

- Adding support for filtering presence in Clinvar.
  The user has to enable the filter and can then select the
- Fixing pedigree display in filter form
- Splitting "${person}_ad" field into "\*_ad_het" and "\*ad_hom", also adjusting tests etc.
- Fixing clinvar queries (was a ``+/-1`` error)
- Adding more comprehensive tests for views and query.
- Fixing bug in ``file_export`` module caused by not adjusting to SQL Alchemy filter querying.
- Added various tests and fixed smaller bugs.
- Adding ``VariantSmallComment`` and ``VariantFlags`` models for user annotation of variants.
- Adding clinvar-centric support for easily screening variants for relevant Clinvar entries.
- The importer now also writes ``"has_gt_fields"`` key to Pedigree lines.
- The templates, views, and query generation now also heed ``"has_gt_fields"`` field.
- Adding migration that automatically adds the ``"has_gt_fields"``.
- Adding back display of search bar.
- Integrating search functionality for ``variants`` app.
- Self-hosting CSS, JS, etc. now.
- Adding ``search_tokens`` to ``Case`` with lower-case IDs.

------
v0.4.0
------

End-User Summary
================

This is the first release made available to the public.
Major features include

- Categories and projects as well as access control assignment is taken from the main SODAR site.
  Organizing projects and users is done in the main SODAR site.
- Variant filtration can be done on a large number of attributes.
  This includes a specialized *compound recessive* filter.
- Filtration results can be converted into TSV/XLSX files for opening in Excel or VCF for further processing.

Full Change List
================

- Sodar-core integration for user and project management
- Download of filter results in TSV, VCF or EXCEL file format
- SQLAlchemy replaces for raw query generation for filter queries
- Heterozygous database entries of frequency databases are now properties of the model
- UI improvements
- Updated and completed database query tests
- Refinement of indices and queries improves filter query performance
- Simplifying import from gts TSV, vars TSV, and PED file in one go
