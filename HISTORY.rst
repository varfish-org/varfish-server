===================
History / Changelog
===================

-----------------
HEAD (unreleased)
-----------------

- Changing display color of relatedness (red indicates error).
- Computing cohort statistics in a transaction.
  This should get rid of possible inconsistencies.

------
v0.9.3
------

This is a bug fix release.

- Removing restriction on single comment per variant.
- Improving display of sex errors.

------
v0.9.2
------

This is a bugfix release.

- Fixing error in displaying variants statistics for empty project.
- Improving relationship error display.
- Putting "sibling-sibling" instead of "parent-child" where it belongs.
- Fixing problem with MutationDistiller submission.
- Fixing ClinVar form.
- Adding gene link-out to HGMD.

------
v0.9.1
------

This release fixes some bugs introduced in v0.9.0.

Full Change List
================

- Adding missing dependency on ``django_redis``.
- Fixing counting in project-wide statistics computation.
- Fixing references to ``pedigree_relatedness``.
- Fixing sex display in template, sex error message "male" where "female should be".
- Fixing sex assignment in sex scatter plot.

------
v0.9.0
------

This release adds project-wide statistics and variant querying.

End-User Summary
================

- You can now see project-wide case QC statistics plots on your project's Case List.
- You can now perform project-wide queries to your variants and also export them to TSV and Excel files.

Full Change List
================

- Added models for storing project-wide statistics, job code for creating this, views for viewing etc.
- Adjusting the existing plot and model code to accommodate for this.
- Refactoring filtration form class into composition from multiple mixins.
- Refactoring small variant query model to use abstract base class and add query model for project-wide queries.
- Implementing download as tabular data for project-wide filtration.
- Improving index structure for project-wide queries with gene white-lists.

------
v0.8.0
------

This release adds variant statistics and quality control features.

End-User Summary
================

- Gathering an extended set of statistics for each individuals in a case.
- Inconsistencies within pedigree and between pedigree and variant information displayed throughout UI.
- Several statistics and quality control plots are displayed on the case details page.

Full Change List
================

- Adding ``var_qc_stats`` module with analysis algorithms similar to (Pedersen and Quinlan, 2017).
- Adding models for gathering per-sample and per-sample-pair statistics.
- Display statistics results on case detail page in tableas and plots.
- Highlighting of consistency and sanity check errors throughout the views.
- Importer computes statistics for new cases, migration adds them to existing cases.

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
