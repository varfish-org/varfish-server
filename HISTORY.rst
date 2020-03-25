===================
History / Changelog
===================

-----------------
HEAD (unreleased)
-----------------

End-User Summary
================

- Added preset for mitochondrial filter settings.
- Fixed bug where HPO name wasn't displayed in textarea after reloading page.
- Added possibility to enter OMIM terms in phenotype prioritization filter.
- Added maximal exon distance field to ``Variants & Effects`` tab.
- Adapted ``HelixMTdb`` filter settings, allowing to differntiate between hetero- and homoplasmy counts.
- Increased default max collective background count in SV filter from 0 to 5.
- Included lists of genomic regions, black and white genelists and reworked HPO list in table header as response for what was filtered for (if set).
- Added ``molecular`` assessment flag for variant classification.
- Fixed bug where activated mitochondrial frequency filter didn't include variants that had no frequency database entry.
- Added inheritance preset and quick preset for X recessive filter.
- Removed VariantValidator link-out.
- Now smallvariant comments, flags and ACMG are updating in the smallvariant details once submitted.
- Deleting a case (only possible as root) runs now as background job.
- Fixed bug in compound heterozygous filter with parents in pedigree but without genotype that resulted in variants in genes that didn't match the pattern.
- Bumped django version to 1.11.28 and sodar core version to bug fix commit.
- Fixed bug where structural variant results were not displayed anymore after introduced ``molecular`` assessment flag.
- Fixed bug where variant comments and flags popup was not shown in structural variant results after updating smallvariant details on the fly.
- Made ``Download as File`` and ``Submit to MutationDistiller`` buttons more promiment.
- Adapted preset settings for ``ClinVar Pathogenic`` setting.
- Finalized mitochondrial presets.
- Added identifier to results table and smallvariant details when mitochondrial variant is located in D-loop region in mtDB.
- Fixed per-sample metrics in case variant control.
- Made ACMG and Beacon popover disappear when clicking anywhere.
- Fixed bug when a filter setting with multiple HPO terms resulted in only showing one HPO term after reloading the page.
- Extended information when entering the filter page and no previous filter job existed.
- Disabled relatedness plot for singletons.
- Replaced tables in case QC with downloadable TSV files.
- QC charts should now be displayed properly.
- Consolidated flags, comments and ACMG rating into one table in the case detail view, with one table for small variants and one for structural variants.
- Added VariantValidator link to submit to REST API.
- Fixed alignment stats in project-wide QC.

Full Change List
================

- Added preset for mitochondrial filter settings.
- Fixed bug where HPO name wasn't displayed in textarea after reloading page.
  HPO terms are now also checked for validity in textbox on the fly.
- Added possibility to enter OMIM terms in phenotype prioritization filter.
  The same textbox as for HPO terms also accepts OMIM terms now.
- Added maximal exon distance field to ``Variants & Effects`` tab.
- (Hopefully) fixing importer bug (#524).
- Adapted ``HelixMTdb`` filter settings, allowing to differntiate between hetero- and homoplasmy counts.
- Fixed inactive filter button to switch from SV filter to small variant filter.
- Increased default max collective background count in SV filter from 0 to 5.
- Included lists of genomic regions, black and white genelists and reworked HPO list in table header as response for what was filtered for (if set).
- Added ``molecular`` assessment flag for variant classification.
- Fixed bug where activated mitochondrial frequency filter didn't include variants that had no frequency database entry.
- Added inheritance preset and quick preset for X recessive filter.
- Removed VariantValidator link-out.
- Now smallvariant comments, flags and ACMG are updating in the smallvariant details once submitted.
- Deleting a case (only possible as root) runs now as background job.
- Fixed bug in compound heterozygous filter with parents in pedigree but without genotype that resulted in variants in genes that didn't match the pattern.
- Bumped django version to 1.11.28 and sodar core version to bug fix commit.
- Fixed bug where structural variant results were not displayed anymore after introduced ``molecular`` assessment flag.
- Fixed bug where variant comments and flags popup was not shown in structural variant results after updating smallvariant details on the fly.
- Made ``Download as File`` and ``Submit to MutationDistiller`` buttons more promiment.
- Adapted preset settings for ``ClinVar Pathogenic`` setting.
- Finalized mitochondrial presets.
- Added identifier to results table and smallvariant details when mitochondrial variant is located in D-loop region in mtDB.
- Fixed per-sample metrics in case variant control.
- Made ACMG and Beacon popover disappear when clicking anywhere.
- Fixed bug when a filter setting with multiple HPO terms resulted in only showing one HPO term after reloading the page.
- Extended information when entering the filter page and no previous filter job existed.
- Added lodash javascript to static.
- Disabled relatedness plot for singletons.
- Replaced tables in case QC with downloadable TSV files.
- QC charts should now be displayed properly.
- Consolidated flags, comments and ACMG rating into one table in the case detail view, with one table for small variants and one for structural variants.
- Added VariantValidator link to submit to REST API.
- Fixed alignment stats in project-wide QC.

-------
v0.20.0
-------

End-User Summary
================

- Added count of annotations to case detail view in ``Variant Annotation`` tab.
- De-novo quick preset now selects ``AA change, splicing (default)`` for sub-preset ``Impact``, instead of ``all coding, deep intronic``.
- Added project-wide option to disable pedigree sex check.
- Added button to case detail and case list to fix sex errors in pedigree for case or project-wide.
- Added command ``import_cases_bulk`` for case bulk import, reading arguments from a JSON file.
- Entering and suggeting HPO terms now requires at least 3 typed charaters.
- Fixed broken variant details page when an HPO id had no matching HPO name.
- Fixed bug in joint filtration filter view where previous genomic regions where not properly restored in the form.
- Fixed bug that lead to an AJAX error in the filter view when previous filter results failed to load because the variants of a case were deleted in the meantime.
- Entering the filter view is now only possible when there are variants and a variant set.
  When there are variant reported but no variant set, a warning in form of a small red icon next to the number of variants is displayed, complaining about an inconsistent state.
- In case of errors, you can now give feedback in a form via Sentry.
- Fixed bug that occurred during project file export and MutationTaster pathogenicity scoring and a variant was multiple times in the query string for mutation taster.
- Adding REST API for Cases.
- Adding site app for API token management.
- Added frequency databases for mitochondrial chromosome, providing frequency information in the small variant details.
- Fixed periodic tasks (contained clean-up jobs) and fixed tests for periodic tasks.
- Adding REST API for Cases and uploading cases.
- Adding GA4GH beacon button to variant list row and details.
  Note that this must be activated in the user profile settings.
- Added filter support to queries and to filter form for mitochondrial genome.

Full Change List
================

- Added count of annotations to case detail view in ``Variant Annotation`` tab.
- De-novo quick preset now selects ``AA change, splicing (default)`` for sub-preset ``Impact``, instead of ``all coding, deep intronic``.
- Added project-wide option to disable pedigree sex check.
- Added button to case detail and case list to fix sex errors in pedigree for case or project-wide.
- Added command ``import_cases_bulk`` for case bulk import, reading arguments from a JSON file.
- Entering and suggeting HPO terms now requires at least 3 typed charaters.
  Also only sending the query if the HPO term string changed to reduce number of executed database queries.
- Fixed broken variant details page when an HPO id had no matching HPO name.
  This happened when gathering HPO names, retrieving HPO id from ``Hpo`` database given the OMIM id and then the name from ``HpoName``.
  The databases ``Hpo`` and ``HpoName`` don't match necessarly via ``hpo_id``, in this case because of an obsolete HPO id ``HP:0031988``.
  Now reporting ``"unknown"`` for the name instead of ``None`` which broke the sorting routine.
- Fixed bug in ``ProjectCasesFilterView`` where previous genomic regions where not properly restored in the form.
- Fixed bug that lead to an AJAX error in the filter view when previous filter results failed to load because the variants of a case were deleted in the meantime.
- Entering the filter view is now only possible when there are variants and a variant set.
  When there are variant reported but no variant set, a warning in form of a small red icon next to the number of variants is displayed, complaining about an inconsistent state.
- Using latest sentry SDK client.
- Fixed bug that occurred during project file export and MutationTaster pathogenicity scoring and a variant was multiple times in the query string for mutation taster.
- Adding REST API for Cases.
- Copying over token management app from Digestiflow.
- Added frequency databases ``mtDB``, ``HelixMTdb`` and ``MITOMAP`` for mitochondrial chromosome.
  Frequency information is provided in the small variant detail view.
- Fixed periodic tasks (contained clean-up jobs) and fixed tests for periodic tasks.
- Adding REST API for ``Case``s.
- Extending ``importer`` app with API to upload annotated TSV files and models to support this.
- Adding GA4GH beacon button to variant list row and details.
  Note that this must be activated in the user profile settings.
- Added filter support to queries and to filter form for mitochondrial genome.

-------
v0.19.0
-------

End-User Summary
================

- Added inhouse frequency information to variant detail page.
- Added link-out in locus dropdown menu in results table to VariantValidator.
- Added filter-by-status dropdown menu to case overview page.
- Added link-out to pubmed in NCBI gene RIF list in variant details view.
- Fixing syncing project with upstream SODAR project.
- Added controls to gnomad genomes and gnomad exomes frequencies in variant details view.
- Adding more HiPhive variants.
- Replacing old global presets with one preset per filter category.
- Added recessive, homozygous recessive and denovo filter to genotype settings.
- Entering HPO terms received a typeahead feature and the input is organized in tags/badges.
- Import of background database now less memory intensive.
- Added project-wide alignment statistics.
- Added ``django_su`` to allow superusers to temporarily take on the identity of another user.
- Fixed bug in which some variants in comphet mode only had one variant in results list.
- Added user-definable, project-specific tags to be attached to a case.
  Enter them in the project settings, use them in the case details page.
- Added alert fields for all ajax calls.
- Removed (non function-disturbing) javascript error when pre-loaded HPO terms were decorated into tags.
- Fixed coloring of rows when flags have been set.
- Fixed dominant/denovo genotype preset.
- Minor adjustments/renamings to presets.
- Link-out to genomics england panelapp.
- Fixed partly broken error decoration on hidden tabs on field input errors.
- Added Kiosk mode.
- Fixed bug when exporting a file with enabled pathogenicity scoring led to an error.
- Entering filter form without previous settings now sets default settings correctly.
- Switched to SODAR core v0.7.1
- HPO terms are now pastable, especially from SODAR.
- Some UI cleanup and refinements, adding shortcut links.
- Large speed up for file export queries.
- Fixed UI bug when selecting ``ClinVar only`` as flags.
- Added link-out to variant when present in ClinVar.
- Fixed broken SV filter button in smallvariant filter form.
- Added link-out to case from import bg job detail page.
- Added ``recessive`` quick presets setting.
- Added functionality to delete small variants and structural variants of a case separately.
- Fixed bug in which deleting a case didn't delete the sodar core background jobs.
- Old variants stats data is not displayed anymore in case QC overview when case is re-imported.

Full Change List
================

- Added inhouse frequency information to variant detail page.
- Added link-out in locus dropdown menu in results table to VariantValidator.
  To be able to construct the link, ``refseq_hgvs_c`` and ``refseq_transcript_id`` are also exported in query.
- Added filter-by-status dropdown menu to case overview page.
  With this, the bootstrap addon ``bootstrap-select`` was added to the static folder.
- Added link-out to pubmed in NCBI gene RIF list in variant details view.
  For this, ``NcbiGeneRif`` table was extended with a ``pubmed_ids`` field.
- Fixing syncing project with upstream SODAR project.
- Added controls to gnomad genomes and gnomad exomes frequencies in the database table by extending the fields.
  Added controls to frequency table in variant details view.
- Improving HiPhive integration:
    - Adding human, human/mouse similarity search.
    - Using POST request to Exomiser to increase maximal number of genes.
- Replacing old global presets with one preset per filter category.
- Using ISA-tab for syncing with upstream project.
- Added recessive, homozygous recessive and denovo filter to genotype settings.
  Homozygous recessive and denovo filter are JS code re-setting values in dropdown boxes.
  Recessive filter behaves as comp het filter UI-wise, but joins results of both homozygous and compound heterozygous filter internally.
- Entering HPO terms received a typeahead feature and the input is organized in tags/badges.
- Import of background database now less memory intensive by disabling autovacuum option during import and removing atomic transactions.
  Instead, tables are emptied by genome release in case of failure in import.
- Added project-wide alignment statistics.
- Added ``django_su`` to allow superusers to temporarily take on the identity of another user.
- Fixed bug in which some variants in comphet mode only had one variant in results list.
  The hgmd query was able to create multiple entries for one variant which was reduced to one entry in the resulting list.
  To correct for that, the range query was fixed and the grouping in the lateral join was removed.
- Added user-definable, project-specific tags to be attached to a case.
- Added alert fields for all ajax calls.
- Removed javascript error when pre-loaded HPO terms were decorated into tags.
- Removed (non function-disturbing) javascript error when pre-loaded HPO terms were decorated into tags.
- Fixed coloring of rows when flags have been set.
  When summary is not set but other flags, the row is colored in gray to represent a WIP state.
  Coloring happens now immediately and not only when page is re-loaded.
- Fixed dominant/denovo genotype preset.
- Minor adjustments/renamings to presets.
- Link-out to genomics england panelapp.
- Fixed partly broken error decoration on hidden tabs on field input errors.
- Introduced bigint fields into postgres sequences counter for smallvariant, smallvariantquery_query_results and projectcasessmallvariantquery_query_results tables.
- Added Kiosk mode.
- Fixed bug when exporting a file with enabled pathogenicity scoring led to an error.
- Entering filter form without previous settings now sets default settings correctly.
- Switched to SODAR core v0.7.1
- Changing default partition count to 16.
- Allowing users to put a text on the login page.
- Renaming partitioned SV tables, making logged again.
- HPO terms are now pastable, especially from SODAR.
- Some UI cleanup and refinements, adding shortcut links.
- Large speed up for file export queries by adding indices and columns to HGNC and KnownGeneAA table.
- Fixed UI bug when selecting ``ClinVar only`` as flags.
- Added link-out to variant when present in ClinVar by adding the SCV field from the HGNC database to the query.
- Fixed broken SV filter button in smallvariant filter form.
- Added link-out to case from import bg job detail page.
- Added ``recessive`` quick presets setting.
- Added functionality to delete small variants and structural variants of a case separately.
- Fixed bug in which deleting a case didn't delete the sodar core background jobs.
- Old variants stats data is not displayed anymore in case QC overview when case is re-imported.

-------
v0.18.0
-------

End-User Summary
================

- Added caching for pathogenicity scores api results.
- Added column to the project wide filter results table that displays the number of affected cases per gene.
- Enabled pathogenicity scoring for project-wide filtration.
- Added LOEUF gnomAD constraint column to results table.
- Added link-out to MetaDome in results table.

Full Change List
================

- Added new database tables ``CaddPathogenicityScoreCache``, ``UmdPathogenicityScoreCache``, ``MutationtasterPathogenicityScoreCache`` to cache pathogenicity scores api results.
- Added column to the project wide filter results table that displays the number of affected cases per gene.
  I.e. the cases (not samples) that have a variant in a gene are counted and reported.
- Enabled pathogenicity scoring for project-wide filtration.
  This introduced a new table ``ProjectCasesSmallVariantQueryVariantScores`` to store the scoring results for a query.
- Added LOEUF gnomAD constraint column to results table.
- Added link-out to MetaDome in results table.

-------
v0.17.6
-------

End-User Summary
================

- MutationTaster scoring now able to score InDels.
- MutationTaster rank now displayed as numbers, not as stars, with -1 corresponding to an error during scoring.
- Adding "closed uncertain" state.
- Project-wide filtration allows for comp het filter for individual families.

Full Change List
================

- MutationTaster scoring now able to score InDels.
- MutationTaster rank now displayed as numbers, not as stars.
  Rank -1 and probability -1 correspond to error during MutationTaster ranking or empty results from MutationTaster.
- Improving display and logging in alignment QC import.
- Adding "closed uncertain" state.
- Project-wide filtration allows for comp het filter for individual families.

-------
v0.17.5
-------

End-User Summary
================

- BAM statistics (including target coverage information) can now be imported and displayed.
- Mitochondrial variants can now be properly displayed.
- Added ``Delete Case`` button and functionality to case overview, only visible for superusers.
- Fixed error response when MutationDistiller submission wasn't submitted with a single individual.
- Now using 404 & 500 error page from sodar core.
- Visual error response on tabs is now more prominent.
- Included MutationTaster as additional pathogenicity score.
- Included UMD-Predictor as additional pathogenicity score.
- Project-wide filter now applicable when the project contains cases with no small variants (e.g. completely empty or only SVs).
- Ignoring option ``remove if in dbSNP`` when ``ClinVar membership required`` is activated as every ClinVar entry has a dbSNP id.
- Fixed indices on ``SmallVariantFlags`` and ``SmallVariantComment`` and introduced indices for ``ExacConstraints`` and ``GnomadConstraints`` that sped up large queries significantly.
- Fixed issue where gene dropdown menu was overlayed by sticky top.
- Adding progress bar on top of case list.
- Improving case list and detail overview page layout and usability.
- Upgrade of the SODAR-core library app, includes various improvements such background job pagination and improvements to membership management.
- Included tables for converting refseq and ensembl gene ids to gene symbols.
- Added warning about missing UMD indel scoring.
- Now sorting comments and flags in the case overview by chromosomal position.
- Now sorting HPO terms in variant detail view alphabetically.
- Improved pubmed linkout string.
- Added EnsEMBL and ClinVar linkouts to gene dropdown menu in results list.
- Added 3 more variant flags: no known disease association, variant does segregate, variant doesn't segregate.
- Compound heterozygous filter is now applicable to singletons and index patients with only one parent.

Full Change List
================

- Adding code for importing, storing, and displaying BAM quality control values.
- Fixing ``urls`` configuration bug preventing chrMT matches.
- Added ``Delete Case`` button and functionality to case overview, only visible for superusers.
  Deletes record from ``Case`` and variants from ``SmallVariant``, ``StructuralVariant`` and ``StructuralVariantGeneAnnotation`` associated with this case.
- Fixed error response when MutationDistiller submission wasn't submitted with a single individual.
  Error is now displayed via ``messages`` after reloading the filter page.
  All form errors that are raised during submission of file export or to MutationTaster are handled now this way.
- Now using 404 & 500 error page from sodar core.
- Visual error response on tabs is now more prominent.
- Included MutationTaster as additional pathogenicity score.
- Included UMD-Predictor as additional pathogenicity score.
- Project-wide filter now applicable when the project contains cases with no small variants (e.g. completely empty or only SVs).
- Ignoring option ``remove if in dbSNP`` when ``ClinVar membership required`` is activated as every ClinVar entry has a dbSNP id.
- Fixed indices on ``SmallVariantFlags`` and ``SmallVariantComment`` and introduced indices for ``ExacConstraints`` and ``GnomadConstraints`` that sped up large queries significantly.
- Fixed issue where gene dropdown menu was overlayed by sticky top.
- Adding progress bar on top of case list.
- Improving case list and detail overview page layout and usability.
- Upgraded to SODAR core v0.7.0.
- Included tables ``RefseqToGeneSymbol`` and ``EnsemblToGeneSymbol`` convert gene ids to gene symbols to get a better coverage of gene symbols.
- Added warning about missing UMD indel scoring.
- Now sorting comments and flags in the case overview by chromosomal position.
  For this, a ``chromosome_no`` field was introduced in ``SmallVariantComments`` and ``SmallVariantFlags`` that is automatically filled when record is saved, derived from ``chromosome`` field.
- Now sorting HPO terms in variant detail view alphabetically.
- Improved pubmed linkout string.
- Added EnsEMBL and ClinVar linkouts to gene dropdown menu in results list.
- Added 3 more variant flags: no known disease association, variant does segregate, variant doesn't segregate.
- Compound heterozygous filter is now applicable to singletons and index patients with only one parent.

-------
v0.17.4
-------

End-User Summary
================

- Fixed bug in exporting files when pathogencity scoring is activated.
- Added IGV button to small/structural comment list in case overview.
- Adapted to new CADD REST API implementation.

Full Change List
================

- Fixed function call to missing function in exporting files when pathogencity scoring is activated.
- Added IGV button to small/structural comment list in case overview.
- Adapted to new CADD REST API implementation.
- Adding generic ``info`` field to small variants and fields for distance to refseq/ensembl exons.
  The import is augmented such that the fields are filled with appropriate empty/null values when importing TSV files that don't have this field yet.

-------
v0.17.3
-------

End-User Summary
================

- Improving QC plot performance.
- Displaying case statistics in project list.
- Removed ClinVar view and added alternative column switch to smallvariant results table.
- ClinVar settings were extended to allow filtering for origin ``somatic`` and ``germline``.
- When ClinVar membership is NOT required, variants that have origin ``somatic`` and no ``germline`` in ClinVar, are removed.
- Improved sorting of results table for ``gene`` and chromosomal position column.
- Fixed bug where settings of the previous query wasn't restored for certain fields.
- Fixed bug where ClinVar data could break rendering of results table template.
- Improved speed of queries.
- Invalid form data now more prominently placed.
- Improved joining of HGNC information for refseq transcripts to not ignore borderd cases.
- Max AD field in quality filter is now also applied to genotype 0/0.
- Minor fixes in case overview comments/flags/acmg tables.
- Fixed issue in SV results table where columns were missing when the genotype was missing.
- Comments on variants are now editable and deletable, in the case detail view as well as the variant detail view.
- Case comments are now edtiable.
- Fixed pathogenicity and phenotype score column headings in results table.

Full Change List
================

- Using ``"scattergl"`` for QC plots which leads to a speedup.
- Making the large tables ``UNLOGGED`` to improve bulk insertion performance.
- Displaying case statistics in project list.
- Removed ClinVar view and added alternative column switch to smallvariant results table.
  All models, urls, views, queries and templates concerning ClinVar view were removed.
  SmallVariant queries now join ClinVar information and display them via switch in the UI.
- ClinVar settings were extended to allow filtering for origin ``somatic`` and ``germline``.
- When ClinVar membership is NOT required, variants that have origin ``somatic`` and no ``germline`` in ClinVar, are removed.
- Results table is now sortable by chromosome and position.
  And by ``gene`` column using the following keys in that given order: ACMG membership, HPO inheritance term, gene name.
  And by ``sign. & rating`` column using the following keys in that given order: significance, rating.
- Fixed bug where settings of the previous query were overwritten by a JavaScript routine and appeared to be lost.
- Fixed bug where unexpected ClinVar significance crashed the template tags.
- Added index on ``human_entrez_id`` field to ``MgiMapping`` materialized view to speed up the join to the results table.
- Invalid form data is now displayed as boxes rather than tooltips.
- Joining of the HGNC information for RefSeq transcripts additionally directly via HGNC to improve results.
- Max AD field in quality filter is now also applied to genotype 0/0.
- Minor fixes in case overview comments/flags/acmg tables.
- Fixed issue in SV results table where columns were missing when the genotype was missing.
- Main JavaScript functionality transferred from HTML to static JS files.
- Comments on variants are now editable and deletable, in the case detail view as well as the variant detail view.
- Case comments are now edtiable.
- Moved and consolidated further JS code from HTML to JS files.
- Fixed pathogenicity and phenotype score column headings in results table.

-------
v0.17.2
-------

End-User Summary
================

- Improving case list and case detail views.
- Adjusting chrX het threshold for telling male/female apart.

Full Change List
================

- Shuffling around case detail view a bit.
- Adding icons for case status.
- Adjusting chrX het threshold for telling male/female apart.

-------
v0.17.1
-------

End-User Summary
================

- Syncing with upstream now also checks parents.
- Fixing saving of ACMG rating.
- Increasing maximal number of characters in gene whitelist to 1 million.
- Fixing QC display issues for cases without variants.
- Fixing UI error where tab wasn't selectable after invalid data input.
- Improving gene and variant detail display.
- Adding installation manual.

Full Change List
================

- Syncing with upstream now also checks parents.
- Fixing template, form, and model for ACMG rating (adjust to using start/end/bin fields).
- Increasing maximal number of characters in gene whitelist to 1 million.
- Fixing QC display issues for cases without variants.
- Fixing UI error where tab wasn't selectable after invalid data input.
- Improving gene and variant detail display.
- Adding installation manual.

-------
v0.17.0
-------

End-User Summary
================

- Fixing problems with link-out to varSEAK.
- UI improvement for the compound heterozygous mode.
- Fixing bug in genomic region filter form that took only the last character of chromosome names.
- Fixing overflow bug in genotype and quality tab when presenting more individuals than would fit in the form.
- Fixing genotype settings pre-selector dropdown that was trapped in parent container and possibly not entirely accessible.
- Added editable ``notes`` and ``status`` fields to case detail view to enable the user to take a note/summarize the case.
- Added support to add multiple comments by different users to a case in the case detail view.
- Fixed bug where using genotype presets wasn't fully executed while in comp. het. mode.
- Fixed bug where the genomic region form wasn't properly reconstructed when only a chromosome was given.
- Properly sorting results now by chromomsome in order as expected (numerical followed by X, Y, MT).
- Included MGI mouse gene link-out in gene dropdown menu in result list.
- Fixed bug where the filter button wasn't disabled when the selected variant set wasn't in state ``active``.
- Renamed ``index`` field in genotype dropdown to ``c/h index`` to indicate comp het mode.
- Fixing bug in retreiving comments on structural variants.

Full Change List
================

- URL-escaping ``hgvs_p`` to varSEAK.
- Compound heterozygous mode is now activated via the GT field selection that offers an ``index`` entry for potential index patients.
  This is a UI/Javascript improvement and does not affect the code of the query except that setting an index enables the filter,
  contrary to before where there was an additional boolean field that enabled the mode.
- Fixing regex bug in genomic region field of the filter form that took only the last charactar of a chromosome name.
  Therefore it affected regions with chromosome names with more than one character (e.g. '10', '11', ...)
- Fixing overflow bug in genotype and quality tab when presenting more individuals than would fit in the form.
- Fixing genotype settings pre-selector dropdown that was trapped in parent container and possibly not entirely accessible.
- Added editable ``notes`` and ``status`` fields to ``Case`` model to enable the user in the case detail view to take notes and assign a status to the case.
- Fixed displaying of ``status`` in case detail view when it was never set.
- Added model ``CaseComments`` to enable assigning comments to a case by different users in the case detail view.
- Fixed bug where using genotype presets wasn't fully executed while in comp. het. mode.
- Fixed bug where the genomic region form wasn't properly reconstructed when only a chromosome was given.
- Sorting results now by the numerical representation of the chromosome.
- Included MGI mouse gene link-out in gene dropdown menu in result list.
  This is accomplished by introducing new table ``MgiHomMouseHumanSequence`` and a condensing materialized view ``MgiMapping`` that maps ``entrez_id`` to ``MGI ID``.
- Removed ``annotation`` app.
- Fixed bug where the filter button wasn't disabled when the selected variant set wasn't in state ``active``.
- Added management command ``rebuild_project_case_stats`` to rebuild stats of all cases of a given project.
- Import of database tables now handles non-existing entries in a more logical way.
- Making variant partion count come from environment variable (#368).
- Renamed ``index`` field in genotype dropdown to ``c/h index`` to indicate comp het mode.
- Fixed bug that replaced missing form fields in old queries with default settings.
- Merged ``import_sv_dbs`` into ``import_tables`` manage command.
- Fixing bug in retreiving comments on structural variants.
- Fixing recomputation of variant stats that now properly handles json decoding.
- Adding installation manual.

-------
v0.16.1
-------

End-User Summary
================

- Cases with no variants or no associated variant set can't be filtered anymore.

Full Change List
================

- Cases with no variants or no associated variant set caused queries to return all variants.
  This bug was fixed by disabling the filter button (UI) or throwing an error query) if the query is executed.

-------
v0.16.0
-------

End-User Summary
================

- Genomic regions now also able to filter only by chromosome.
- Added preset selector for genotypes, setting affected or unaffected individuals to the selected setting.
- dbSNP ID in file export is now set to ``None`` instead of an empty field.
- Fixed sorting issues with ranks and scores.
- Added quality field to set MAX allelic depth (AD) for filtering variants (hom or ref).
  Default is unset, i.e. filtering behaviour as usual.
  Only quality setting that doesn't require a value.
- Added main navigation as dropdown menu for smaller screen sizes.
- Added template settings for quality filter form to copy to each individual, or affectded/unaffected.
- Fixed bug that occurred during file export with activated gene prioritization.
- Improved database connection to avoid occasional JSON field retrieval errors.

Full Change List
================

- Genomic regions filter accepts now only chromosome as region, internally setting start/end positions to 0/INT_MAX values.
- Structural variant databases are now imported in the same style as the small variant databases.
- Removed ``model_support.py`` file from variants app.
- Added preset selector for genotypes, setting affected or unaffected individuals to the selected setting.
- dbSNP ID in file export is now set to ``None`` instead of an empty field.
- Ranks in the results table are now displayed without the hash tag to make them properly sortable.
  Pathogenicity and phenotype scores in the results table now sort in a numerical order.
  Ranks and scores are now in separate fields.
- Small variant filter now considers set id together with case id.
- Removed remaining fixtures from ``test_submit_filter.py``
- Quality filter now can filter variants for max allelic depth.
- Added main navigation as dropdown menu for smaller screen sizes.
- Added template settings for quality filter form to copy to each individual, or affectded/unaffected.
- Fixed function call of gene prioritization function in file export task causing file export to break when gene prioritization was activated.
- Remove switching psycopg2 JSON (de)serializer during database query execution to avoid occasional JSON field retrieval errors.
  Instead, replace the JSON (de)serializers for sqlalchemy and leave it to psycopg2 to take care of this.
- Increased length of ``Case.index`` field from 32 to 512 chars.

-------
v0.15.6
-------

End-User Summary
================

- Row colouring in results table for commented and flagged variants is now back again.

Full Change List
================

- Removing ``Annotation`` model.
- Fixed importer bug where info wasn't imported when table was newly imported and ``--force`` flag was set.
- Removed whitening of table rows from DataTables css to prevent it from overwriting our row colouring feature.
- Doing dbSNP import now chromosome-wise to prevent import from timing out.
- Removed old style fixtures from UI tests.

-------
v0.15.5
-------

End-User Summary
================

- Displaying SV coordinates in detail box.
- Displaying family errors in red in "rate of het. calls on chrX" plot.
- Compound het query now allows index selection for all patients with parents, not only sibling of the index.

Full Change List
================

- Displaying SV coordinates in detail box.
- Fixing sex error generation (only using source name).
- Fixing pedigree editor form to use int for sex & affected.
- Compound het query now allows index selection for all patients with parents, not only sibling of the index.

-------
v0.15.4
-------

End-User Summary
================

- ExAC constraints in results table are now displayed.
- Constraints in results table now show consistenly 3 floating points and are sortable.
- Fixing QC plot display.
- Fixing in-house counts in results table (filtering by them worked).
- Fixing filtration with members that have no genotype.
- Fixing SV length display.
- Adjusting filter presets.
- Fixing filtration for in-house filter.
- Changing display to per-transcript effects to table.
- Index patient for compound heterozygous query is now selectable.
- Fixed bug where clinvar report queries didn't select for the case.

Full Change List
================

- Increased SmallVariant table partitioning to modulo 1024.
- ExAC constraints are now joined via ensembl gene id to results table.
- Constraints in results table now show consistenly 3 floating points and are sortable.
- ExAC constraints are now consistent with variant details and in results table.
- Various fixes to QC plot display, some to JS, some to Python/Django views code.
- Clinvar pathogenic genes materialized view gets updated when there is new data imported in one of the dependent tables.
- Making prefetch filter load inhouse counts.
- Fixing filtration with members that have no genotype.
- Making prefetch filter load inhouse counts.
- Fixing filtration with members that have no genotype.
- Adding back fetching of SV length to queries.
- First adjustments of filter presets for NAMSE analyses.
- Fixing coalescing when filtering with in-house filter.
- Changing display to per-transcript effects to table.
- Extended tests to cover missing in-house filter records for existing variants.
- Index patient for compound heterozygous query can be selected.
  Only patients that share the same parents as the original index patients are selectable in addition.
- After reworking the database query structure, clinvar report queries didn't select for the case.

-------
v0.15.3
-------

Bug-fix release.

End-User Summary
================

- none

Full Change List
================

- fixing bug in recomputing small and structural variant counts on importing

-------
v0.15.2
-------

End-User Summary
================

- Fixed broken genomic region filter.
- Making gene information in SV results consistent with display in small variant results.
- ``--force`` parameter for ``import_tables`` now works on all tables.
- Resulting table is now sortable.
- Fixed broken EnsEMBL link-out.
- Added OMIM gene information to gene card in variant details view.
- Refactored database small variant database queries.
- Adding case and donor counts to project list.
- QC plots are now loaded asynchronously.
  This should improve page loading time for the case and project overview pages.
- Adding inheritance mode information to results table.
- Admins/superusers can now update case information and pedigrees.
- Projects can now synchronise (check) with upstream SODAR sites, only admins/superusers can trigger this.
- Adapting SmallVariants and SmallVariant DBs to new start-end coordinates and UCSC binning.
- Fixed frequency table in SmallVariant details that had wrong names assigned to columns and ``total`` values were not present.
- Added pLI score to variant details constraint information.
- Added constraints information column with selector to results table.

Full Change List
================

- Increased view test coverage to 100%.
- Unification of gene information display between SVs and small variants.
- Fixed bug that wrongly parsed genomic regions and resulted in filter reporting nothing while active.
- Small fix to small variant import.
- Extended ``--force`` parameter for ``import_tables`` command to be applied to all tables.
- Fixed bug in creating materialized view that prevented setting up database when applying migrations from scratch.
- Added datatables library to add sorting feature to resulting table.
- Fixed broken EnsEMBL link-out.
- Added conversion table RefseqToEnsembl (complementing EnsemblToRefseq).
  Now used in ExAC/gnomAD constraint information when refseq transcript database is selected.
- Gene card in variant details view now show OMIM gene information, i.e. when an OMIM entry is marked as gene in Mim2geneMedgen table.
- "All transcript" annotations now come from Jannovar REST web service instead of the ``Annotation`` model.
- Refactored database small variant database queries.
  The database queries now make full use of lateral joins to keep the nesting flat.
  The code generation part now doesn't use the mixin structure anymore that was intransparent and error-prone.
- Bumping ``sodar_core`` dependency to ``v0.6.1``
    - Showing case and donor counts to project listing.
    - Showing site-wide statistics via ``siteinfo`` app.
- Adding missing ``release`` column to ``KnownGeneAA`` table + adapting queries accordingly.
- Cleaning up and refactoring QC plotting code.
    - Separating plotting JS and data generation Python code.
    - Load data asynchronously.
- Now displaying inheritance mode information for results, based on HPO terms for inheritance and hgnc information.
- Not importing ``Annotation`` data any more.
- Adding view for updating a case.
- Implementing "sync with upstream SODAR site" for projects based on background jobs.
- Removing ``bgjobs`` app in favour of the one from SODAR-core.
- Removing ``containing_bins`` columns.
- Removing ``svs`` tests ``_fixtures.py``.
- Adapting SmallVariants and SmallVariant DBs now containt ``start`` and ``end`` column, replacing ``position``.
  This is for internal queries only, the outside representation for SmallVariants is still via ``position``.
  An additional column ``bin`` for the ucsc binning was included.
- Frequency table in SmallVariant details had wrong names assigned to columns and ``total`` values were not present.
  The values in the columns were 1 column behind of its names, and thus the last column had a name that should have had missing values.
  These missing values were also a bug in that case that ``total`` was not reported (i.e. ``af`` or ``het`` without population).
- Constraints information in variant details now shows also pLI score.
- Now joining constraints information to results table and added selector to display source/metric in one column.
- Fixed: Ensembl transcript ids in SmallVariant list were truncated because of too short database field.
- Importing SVs and small variants is done in a background job now.
- Small variant and SV tables are now partitioned (by case ID).
  This should speedup import as indices are smaller and also each partition can be written to independently.
- ``import_tables`` improvements:
    - can now use threads to import multiple tables at once
    - uses SQL Alchemy instead of Django ORM based deletion
- Refining celery configuration now, assuming queues "import", "query", and "default".
- Removing some redundant indices on frequencies an dbsnp.

-------
v0.15.1
-------

A bug fix release for SV filtration (fixing overlaps).

End-User Summary
================

- Fixed conservation bug (was shown only in 2/3 of all cases).
- Showing small and structural variant count for each case.
- Improving layout of case list (adding sorting and filtering).
- Improved render speed of case list.
- Fixing problem with interval overlaps for structural variant queries.

Full Change List
================

- Increased test coverage to 100% for small variant model support tests.
- Fixed bug in displaying conservation track for all bases in an AA base triplet.
  Only two of three bases were decorated with the conservation track information.
- Fixed bug that Clinvar report didn't support compound heterozygous queries anymore.
- Variant view tests are now running on factory boy.
- Adding tests of SV-related code.
- Also interpreting phased diploid genotypes.
- Improving layout of case list (adding sorting and filtering).
- Improved render speed of case list.
- Fixing UCSC binning overlap queries.
- Adding "For research use only" to login screen.

-------
v0.15.0
-------

The most important change is the change of colors: **Green now means benign and red means pathogenic**.

End-User Summary
================

- Renamed Human Splice Finder to Human Splicing Finder.
- Added "1" and "0" genotype for "variant", "reference", and "non-reference" genotype.
- Added support for WGS CNV calling results to SV filtration.
- Simplifying variant selection for SVs as diploid calls unreliable (it's better to distinguish only variant/reference).
- Changing color meaning: green now means benign/artifact and red means pathogenic/good candidate.
- Adding link-out to varsome
- Adding support for ACMG criteria annotation
- SV filtration: do not set max count in background by default
- SV filtration: display of call properties of XHMM and SV2

Full Change List
================

- Allow import for more than one genotypes/feature effects for structural variants.
- Starting to base fixture creation on factory boy.
- Renamed Human Splice Finder to Human Splicing Finder.
- Added "1" and "0" genotype for "variant", "reference", and "non-reference" genotype.
- Added support for WGS CNV calling results to SV filtration.
- Simplifying selection of variants for SVs.
  Further, also allowing for phased haplotypes (irrelevance in practice until we start interpreting the GATK HC haplotypes in annotator).
- Changing color meaning: green now means benign/artifact and red means pathogenic/good candidate.
- Adding link-out to varsome
- Adding support for ACMG criteria annotation
- Model support tests now running on factory boy.
- SV filtration: do not set max count in background by default
- SV filtration: display of call properties of XHMM and SV2

-------
v0.14.8
-------

Multiple steps towards v0.15.0 milestone.

End-User Summary
================

- Adding link-out to the UMD Predictor (requires users to configure a UMD Predictor API Token).
- Adding user settings feature.
- Improving link-out to PubMed.
- Adding gene display on case overview for flags and comments.
- Added warning icon to results table indicating significant differences in frequency databases.
- Added command to rebuild variant summary materialized view ``rebuild_variant_summary``.
- Added ExAC and gnomAD constraint information to variant details gene card.
- Displaying allelic balance in genotype hover and variant detail fold-out.

Full Change List
================

- Added elapsed time display to ``import_case``
- Speedup deletion of old data using SQL Alchemy for ``import_case``.
- Added indices to hgnc, mim2genemedgen, acmg and hgmd tables.
- Added command to rebuild variant summary materialized view ``rebuild_variant_summary``.
- Adding link-out to PubMed with gene symbol and phenotype term names.
- Improving existing link-out to Entrez Gene if the Entrez gene ID is known.
- Adding user settings through latest SODAR-core feature.
- Adding ``ImportInfo`` to django admin.
- Adding "New Features" button to to the top navigation bar.
- Adding link-out to the UMD Predictor (requires users to configure a UMD Predictor API Token).
- Overlapping gene IDs now displayed for flags and comments on the case overview/detail view.
- Added warning icon to results table when a frequency in a non-selected frequency table is > 0.1.
  Or if hom count is > 50. For inhouse it is only hom > 50 as there is no frequency.
- Added ExAC and gnomAD constraint information to variant details gene card.
  Two new tables were added, ``GnomadConstraint`` and ``ExacConstraint``.
- Displaying allelic balance in genotype hover and variant detail fold-out.
- Removing unique constraint on ``SmallVariant``.
- Fixing case update in the case of the variants being referenced from query results.

-------
v0.14.7
-------

End-User Summary
================

- Bug fix release.

Full Change List
================

- Fixed bug that inhouse frequencies were not joined to resulting table.
- Removed restriction that didn't allow pasting into number fields.

-------
v0.14.6
-------

End-User Summary
================

- Adding experimental filtration of SVs.
- Added names to OMIM IDs in variant detail view.
- Added input check for chromosomal region filter.
- User gets informed about database versions during annotation and in VarFish.
- Added ClinVar information about gene and variant to variant detail view.
- Added selector for preset gene filter lists (HLA, MUC, ACMG).
- Added comments and flags to variant details view.
- Fixed bug that transcripts in variant details view were from RefSeq when EnsEMBL was selected.
- Added icon to variant when RefSeq and EnsEMBL effect predicition differ.
- Adjusted ranking of genes such that equal scores get the same rank assigned.

Full Change List
================

- Adding initial support for filtration of SVs and SV databases.
- Added names to OMIM IDs in variant detail view.
- Added input check for chromosomal region filter.
- Made ImportInfo table not unique for release info.
- Made annotation release info available in case overview.
- Made import release info available in site app accessable from user menu.
- Added materialized view to gather information about pathogenic and likely pathogenic variants in ClinVar.
  This information is displayed in the gene card of the detail view.
- Added ClinVar information about variant to variant detail view.
- Added selector to gene white/blacklist filter, adding common gene lists (HLA, MUC, ACMG) to the filter field.
- Added comments and flags to variant details view.
- Fixed bug that transcripts in variant details view were from RefSeq when EnsEMBL was selected.
- Added icon to variant when RefSeq and EnsEMBL effect predicition for the most pathogenic transcript (in SmallVariant) differ.
- Adjusted ranking of genes such that equal scores in two genes get the same rank assigned.
  In case of the pathogenicity and joint score the highest variant score in a gene represents the gene score.
  The next ranking gene is assigned not the next larger integer but the rank is increased by the number of genes with the same rank.

-------
v0.14.5
-------

End-User Summary
================

- Bug fix release.

Full Change List
================

- Fixed bug that made query slow when black/whitelist filter was used.

-------
v0.14.4
-------

End-User Summary
================

- Fixed bug in comp het filter.
- Fixed bug in displaying correct previous joint filter query.
- Fixed bug in displaying not all HPO terms.
- Added OMIM terms to variant detail view.
- Fixed bug in variant detail view displaying all het counts as zero.
- Fixed colouring of variant effect badges in variant detail view's transcript information.

Full Change List
================

- Fixed bug in comp. het. filter that was caused by downstream inhouse filter.
- Fixed bug that selected previous joint filter query of the user, independet of the project.
- Fixed bug in displaying not all HPO terms.
- Added OMIM terms to variant detail view.
- Fixed bug that the het properties of the frequencies models were not returned when converted to dict.
- Removing old templates.
- Fixed colouring of variant effect badges in variant detail view's transcript information.

-------
v0.14.3
-------

End-User Summary
================

- Fixed bug in displaying gene info with refseq ID.
- Fixed bug in displaying correct number of rows in joint query.
- User interface error response improved.
- Fixed "too many connections" error.
- Added ACMG annotation.

Full Change List
================

- Fixed bug in gene info with refseq ID and symbol in list is now also "rescued".
- Fixed bug in displaying correct number of rows in joint query.
- Improved error response when non-existing genes are entered in white/blacklist.
- Using direct database calls instead of connections to prevent connection leaking.
- New table Acmg added that is joined in main query.
  A small icon in results indicates existence in ACMG.

-------
v0.14.2
-------

End-User Summary
================

- Added strategy to display missing gene symbols
- Allow importing into importinfo table without importing data.
- Added misc option to hide colouring of flagged variant rows.
- Improved effect filter form.
- Extended gene link-outs.
- Fixed bug in pheno/patho rank computation.
- Improved UI responses during requests.

Full Change List
================

- Added new table with mapping Entrez ID to HGNC ID to improve finding of gene symbols.
- Allow importing of meta information of tables that have no data but are used in microservices.
- Added misc option that hides colouring of flagged variant rows and also the bookmark icons.
- Added checkbox group 'nonsense' to effect filter form to group-(un)select certain variant effects.
- Added gene link-out to Human Protein Atlas.
- Fixed incrementor for rank computation of phenotype and pathogenicity score ranks.
- Better UI responses with extended logging during asynchronous calls.
- Project overview now provides link to full cases list.
- Added option to display only variants without dbSNP membership.
- Adapted to SODAR Core 0.5.0
- Fixed length of allowed characters for db info table name.

-------
v0.14.1
-------

End-User Summary
================

- Bug fix release

Full Change List
================

- Fixing bug in the case that no HPO term with an HpoName entry is entered.

-------
v0.14.0
-------

End-User Summary
================

- Added prioritization by pathogenicity using CADD.
- Added support to filter genomic regions.
- Added support for querying for counts within the VarFish database.
- Fixed bug that displayed variants in comphet query results twice.
- Improved UI response.
- Added HPO terms to variant detail view.

Full Change List
================

- Added additional field to specify multiple genomic regions to restrict query.
- Fixed mixed up sex display in genotype filter tab.
- Extended ``SmallVariant`` model to have counts for hom. ref. etc. counts.
- Adding ``SmallVariantSummary`` materialized view and supporting SQL Alchemy query infastructure.
- Adding form and view infrastructure for querying against in-house database.
- Fixed bug in comphet query that executed the query on the results again during fetching, which displayed variants twice.
- Proper error response in asynchronous queries when server is not reachable.
- Fixed broken tooltip information in results table.
- Resubmitting a file export job now remembers the file type, if changed.
- Added integration with in-house CADD REST API (https://github.com/bihealth/cadd-rest-api) similar to Exomiser REST API integration.
- Added HPO terms to variant detail view and queried HPO terms are added to results table header.
- Added tests for filter jobs, including mocks for CADD and Exomiser requests.

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
