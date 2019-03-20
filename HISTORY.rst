===================
History / Changelog
===================

----
HEAD
----

End-User Summary
================

Added support to filter genomic regions.

Full Change List
================

- Added additional field to specify multiple genomic regions to restrict query.
- Fixed mixed up sex display in genotype filter tab.

-------
v0.13.0
-------

End-User Summary
================

Adding initial version of phenotype-based prioritization using the Exomiser REST Prioritiser API.

Full Change List
================

- Adding missing field for exon loss variant to form.
- Comments in view class adjusted.
- Added HPO to disease name mapping.
- Phenotype match scores are added to the file downloads as well.
- Sorting of variants by phenotype match added.
- Added annotation of variants with phenotyping variant score.
- Added tab to the form form entering HPO term IDs.
- Adding settings for enabling configuring REST API URL through environment variables.

-------
v0.12.2
-------

End-User Summary
================

Internal import fixes.

Full Change List
================

- Case updating only removes variant and genotype info instead of replacing case.
- Allowing import of gziped db-info files.

-------
v0.12.1
-------

Bugfix release.

End-User Summary
================

- Fix in clinvar job detail view.

Full Change List
================

- Clinvar job detail view was partially borken and job resubmitting didn't work.

-------
v0.12.0
-------

User experience improvement, tests extended.

End-User Summary
================

- Filtering jobs can now be aborted.
- Proper visual error response in forms.
- Tests for all views completed.
- Variant details now use full table space.
- Clinvar report jobs are now using AJAX as well and are running in background.

Full Change List
================

- Filtering jobs runs now as background job and can be aborted.
- Invalid fields and affiliated tabs are now marked with a red border.
- Deleted empty files from apps.
- Tests for all views completed.
- Bugfix in rendering download results files for ProjectCases.
- Bugfix in template for job detail view.
- Bugfix in listing background jobs for a case.
- Variant details do not load anymore when detail view is closed.
- Variant details now use full table space.
- Flags and comments do not depend on EnsEMBL gene id anymore.
  All traces where removed, including the database column.
- Clinvar jobs now have their own background job model.
  They also use the AJAX query state machine to control job submission and canceling.
- Now using sodar_core v0.4.5
- Warning appears when Micorsoft Internet Explorer is detected.

-------
v0.11.8
-------

Case importer command improved.

End-User Summary
================

- Case import command registers database version that was used during annotation.

Full Change List
================

- Case import also imports annotation release infos into new table.
- Import information now also recognizes the genomebuild.
- Tests for case importer.
- Fixed bug that didn't distinguish gzipped from plain text import files.

-------
v0.11.7
-------

Bugfix release.

End-User Summary
================

- Fixed yet another bug in setting SmallVariantFlags.

Full Change List
================

- Fixing bug that variant flags are displayed no matter the case.

-------
v0.11.6
-------

Bugfix release.

End-User Summary
================

- Fixed another bug in setting SmallVariantFlags.

Full Change List
================

- Fixed bug that under certain conditions reported two variants at the same position as none and failed flag updating.

-------
v0.11.5
-------

Bugfix release.

End-User Summary
================

- Databases import now as Django manage command.
- Fixed bug in loading last query results.
- Fixed bug in setting SmallVariantFlags.

Full Change List
================

- Databases import is now a Django manage command and import commands are removed from the Makefile.
  Instead of one command for each database, a single command imports all databases stated in a config file.
- Fixed bug that displayed last query of user without considering case.
- Fixed bug that under certain conditions reported two variants at the same position as none and failed flag updating.

-------
v0.11.4
-------

This is a quick release to fix a bug in retrieving the results from a filter job.
This was caused by the celery worker in the production system configuration.

End-User Summary
================

- Zooming in QC plot is now supported.
- Fixing bug in delivering filter results.

Full Change List
================

- Replacing Chart.js components by plotly.
  This has the major advantage that zooming into charts is now supported.
  Further, users can now enable and disable plotting of certain data points by clicking.
  This is hugely useful for debugging meta data.
- Allow skipping Selenium tests
- Fixing bug with celery worker for submitting filter jobs affecting production system.

-------
v0.11.3
-------

This release improves the user experience by pushing filter jobs to the background and
load them asynchronously.

End-User Summary
================

- Push filter jobs to the background and povide them via AJAX to not block the UI during execution
- Storing of filter query results
- Load previous filter query results upon filter form page entry

Full Change List
================

- Adapted to SODAR core version 0.4.2
- Unified several empty forms
- Adapted database query for loading previous results
- Unified filter form templates
- Fixed bug in accessing dict without checking availability of key.
- Removed two view tests that have to be replaced in the future for ajax request.
- Fixed bug in displaying time in background job list overview + ordering by timestamp
- Pushing filter job to background
- Loading filter results via AJAX (single case and joint project)
- Loading of previous filter results when entering the filter form

-------
v0.11.2
-------

This is a bug fix release.

End-User Summary
================

- Removed an internal restriction that prevented data import.

Full Change List
================

- Making id fields for ``SmallVariant`` and ``Annotation`` into big integers.
- The importer now supports gzip-ed files.

-------
v0.11.1
-------

- Fixing frequency display, including gnomAD genomes.

-------
v0.11.0
-------

This release adds more textual information about genes to the database and displays it.

End-User Summary
================

- Adding gene summaries and reference-into-function from NCBI Gene database.

Full Change List
================

- Adding models ``NcbiGeneInfo`` and ``NcbiGeneInfo`` in ``geneinfo`` app.
- Displaying this information in the gene details page.

-------
v0.10.0
-------

Accumulation of previous updates.
The main new feature is the improved variant details card below variant rows.

End-User Summary
================

- Fixing variant detail cards below results row.
- Adding row numbers in more places.

Full Change List
================

- Rendering variant details cards on the server instead of filling them out in JS.

------
v0.9.6
------

This release fixes project-roles synchronization from SODAR site.

- Fixing celery setup; syncing projects and roles regularly now.

------
v0.9.5
------

Small additions, fixing MutationDistiller integration.

- Adding link-out to loci in Ensemble, gnomAD, and ExAC.
- Adding link-out for Polyphen 2, Human Splicing Finder, and varSEAK Splicing.
- Project-wide variant recreation registers started state now correctly.
- Fixing URL for MutationDistiller Links.
- Using HTTPS links for ENSEMBL and MutationTaster.

------
v0.9.4
------

Yet another bug fix release.

- Adding missing 5' UTR fields to forms.
- Adding command for rebuilding project stats.
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
