# Changelog

### (towards v2.0.0 before release-please)

- Documenting problem with extra annotations in `20210728` data release (#450). Includes instructions on how to apply patch to get `20210728b`.
- Removing problematic username modification behaviour on login page (#459).
- Displaying login page text from settings again (#458).
- Suppress \"submit to CADD\" and \"submit to SPANR\" buttons for multi-case form (#478). This has not been implemented so far.
- Fixing paths in \"Variant Ingest\" documentation (#472).
- Small extension of \"Resolution proposal\" template (#472).
- Adjusting wrong release name to \"anthenea\" (#479).
- Adding \"show all variant carriers\" feature (#470).
- Properly display the clinvar annotations that we have in the database (#464).
- Adjusting default frequency filters for \"clinvar pathogenic\" filter: remove all threshold (#464).
- Adding note about difference with upstream Clinvar (#464).
- Switching scoring to MutationTaster 85 interface, added back MT 85 link-out alongside MT 2021 link-out (#509).
- CADD setup fix for documentation (#520)
- Made flag filter and flag form nomenclature consistent (#297).
- Updating `utility/*.sh` scripts from \"upstream\" sodar-server (#531).
- Improved developer setup documentation and added Windows installation instructions (#533).
- Skip commit trailer checks for dependabot (#537).
- Fixed broken VariantValidator query (#523).
- Converted not cooperative tooltip to standard title on Filter & Display button (#508).
- Fixed smallvariant flags filter query (#502).
- Added flags `segregates`, `doesnt_segregate` and `no_disease_association` to file export (#502).
- Adjusting path to new varfish-annotator db download (#546).
- Fixing issue with sync-from-remote when no remote is defined (#570).
- Adding feature to enable and configure link-out to HGMD (#576).
- Small variant filtration results now allow to easily look up second hits in the same gene (#573).
- Structural filtration results now allow to easily look up second hits in the same gene (#574).
- Bugfix broken SV filter (#587).
- Fixed bug where Exac and thousand genomes settings were not shown in frequency tab for GRCh37 (#597).
- Form template reports error if genomebuild variable is not set (#607).
- Making `keyvalue` more robust to failure (#613).
- Implement new in-house background database for structural variants (#32).
- Allow to exclude cases from in-house database through project settings (#579).
- Adding distinct de novo genotype setting (#562).
- Adding section presets for SV filtration (#616).
- Adjusting SV filtration presets (#616).
- Fix bug with thousand genomes frequencies in SV filtration (#619).
- Displaying disease gene icon also for SVs (#620).
- Fix bug with gene constraint display for intergenic variants (#620).
- Fix import bug in import\_tables.py (#625).
- De novo quick preset now uses strict quality (#624).
- Create single result row even if multiple clinvar entries (#565).
- Fixing clinvar filter (#296). **This will require an import of the updated Clinvar `20210728c` data (#296).**
- Improving Clinvar filter performance (#635). Database indices were missing, assumedly because of a Django `makemigrations` bug.
- Warning in the case of truncated displayed results (#641).
- Improving Clinvar record aggregation (#640).
- Fixing Docker builds (#660).
- Fixing ClinVar submission XML generation (#677).
- Adding regular task to sync ClinVar submission `Individual` sex from the one from the `Case`.
- Fixing ClinVar export editor timing issues (#667, #668).
- Fixing hemizygous count display in fold-outs (#646).
- Fixing clinvar submission sex/gender update (#686).
- Fixing issue with phenotype name in Clinvar (#689).
- Initial vue.js implementation for small variant filtration (#563).
- Changing ClinVar link-out to VCV entry instead of coordinates (#693).
- Adding unit test for clinvar Vue app (#692).
- Moving clinvar Vue app (#711).
- Bugfix that allow clinvar export submission set deletion (#713).
- Removing dependency on bootstrap-vue package (#716).
- Migrating store dependency from Vuex v3 to Pinia (#720).
- Adding support to create custom gene panels (#723).
- Allow operators to upload per-gene annotations to cases (#575) on import.
- Fixing issue with icon in vue3 variants app (#718).
- Unifying Vue.js/Vite/Rollup builds (#730).
- Switching to use unplugin-icons clinvarexport Vue.js icons (#736).
- Adding support for Storybook.js (#736).
- Display warning icon in filter results table if non-selected frequency is high (#708).
- Adding switch to toggle inline filter help (#700).
- Adding missing tabs for Vue.js variants (#700).
- Fix query schema (#749).
- Bumping sodar-core dependency (#750).
- Migrating case list and details to Vue.js (#743).
- Fix bug in SV background database building (#757).
- Allowing to read clinvar submission reports (#759).
- Fix bug in filtration form with max. exon dist (#753).
- Allow display of extra annos in Vue.js filtration (#755).
- Fix variant icon display (#745).
- Improving installation instructions (#735).
- Implementing case-independent variant annotations (#747).
- Implementing editing of cases in Vue.js (#743).
- Adding user-defined query presets (#776).
- Fixing bug in mutationtaster integration (#790).
- Fixing bug in Vue.js filtration without prior query (#794).
- Fixing bug in SV background database generation (#792).
- Gene prioritization using CADA (Case Annotations and Disorder Annotations) scores (#596)
- Fixing bug in filtering of GQ values that are floats (#816).
- Fixing bug in quick preset loading in vue filter app (#820).
- Adding affected/unaffected preset to genotype form (#821).
- Fixing bug in effect UTR section in vue filter app (#822).
- Removing template settings in quality form tab (#825).
- Removing gene blocklist from vue filter app (#823).

## v1.1.4

### Full Change List

- Installing same postgres version as in docker-compose server (12).

## v1.1.3

### End-User Summary

- Fixing problem with import info display for non-superusers (#431)
- Schema and documentation for case QC info (#428)
- Adding support for HGNC IDs in gene allow lists (#432)
- PanelApp will now populate the gene allow list with HGNC gene IDs (#432)

### Full Change List

- Fixing problem with import info display for non-superusers (#431)
- Schema and documentation for case QC info (#428)
- Adding support for HGNC IDs in gene allow lists (#432)
- PanelApp will now populate the gene allow list with HGNC gene IDs (#432)
- Adding `pg_dump` admin command and documentation (#430)

## v1.1.2

### End-User Summary

- Fixing bug in XLSX export (#417)
- Fixing problem with multi-sample queries (#419)
- Fixing issue with cohort queries (#420)
- Fixing issue with mutationtaster queries (#423)
- Fixing problem with multi-variant update (#419)

### Full Change List

- Fixing bug in corner case of multi variant annotation (#412)
- Updating documentation for v1 release (#410)
- Fixing issue with `fa-solid:refresh` icon (#409)
- Fixing page titles (#409)
- Fixing bug in XLSX export (#417)
- Fixing problem with multi-sample queries (#419). This is done by rolling back adding the `_ClosingWrapper` class. We will need a different approach for the queries than was previously attempted here.
- Fixing issue with cohort queries (#420)
- Fixing issue with mutationtaster queries (#423)
- Fixing problem with multi-variant update (#419)

## v1.1.1

This is the first release candidate of the VarFish \"Anthenea\" release (v1). Importantly, the first stable release for v1 will be v1.2.0 (see [Release Cycle Documentation](https://varfish-server.readthedocs.io/en/latest/release_cycle.html) for a full explanation of version semantics).

This release adds some more indices so the migrations might take some more time.

### End-User Summary

- Fixing problem with CNV import (#386)
- Fixing problem with user annotation of nonexistent variants (#404)

### Full Change List

- Adding REST API for generating query shortcuts (#367)
- Filter queries in REST API to selected case and not all by user
- Fixing problem with CNV import (#386)
- Adding index to improve beaconsite performance (#389)
- Adding missing `mdi` iconset (#284)
- Strip trailing slashes in beconsite entrypoints (#388)
- Documenting PAP setup (#393)
- Adding more indices (#395)
- Fixing discrepancy with REST API query shortcuts (#402)

## v1.1.0

This is the first release candidate of the VarFish \"Anthenea\" release (v1). Importantly, the first stable release for v1 will be v1.2.0 (see [Release Cycle Documentation](https://varfish-server.readthedocs.io/en/latest/release_cycle.html) for a full explanation of version semantics).

Breaking changes, see below.

### End-User Summary

- Fixing Kiosk mode of VarFish.
- Fixing displaying of beacon information in results table.
- Fixing broken flags & comments popup for structural variants.
- Fixing broken search field.
- Extended manual for bug report workflow.
- Fixed recompute of variant stats of large small variant sets.
- Added index for `SmallVariant` model filtering for `case_id` and `set_id`. This may take a while!
- Allowing project owners and delegates to import cases via API (#207).
- Fix for broken link-out into MutationTaster (#240).
- Fixing SODAR Core template inconsistency (#150).
- Imports via API now are only allowed for projects of type `PROJECT` (#237).
- Fixing ensembl gene link-out to wrong genome build (#156).
- Added section for developers in manual (#267).
- Updating Clinvar export schema to 1.7 version (#226).
- Migrated icons to iconify (#208).
- Bumped chrome-driver version (#208).
- VarFish now allows for the import of GRCh38 annotated variants. For this, GRCh38 background data must be imported. Kiosk mode does not support GRCh38 yet. **This is a breaking change, new data and CLI must be used!**
- Added feature to select multiple rows in results to create same annotation (#259)
- Added parameter to Docker entrypoint file to accept number of gunicorn workers
- Extended documentation for how to update specific tables (#177)
- Improving performance of project overview (#303)
- Improving performance of case listing (#304)
- Adding shortcut buttons to phenotype annotation (#289)
- Fixing issue with multiple added variants (#283)
- Implementing several usability improvements for clinvar submission editor (#286)
- Make clinvar UI work with many annotations (#302)
- Fixing CADD annotation (#319)
- Adding mitochondrial inheritance to case phenotype annotation (#325)
- Fix issue with variant annotation export (#328)
- Allowing direct update of variant annotations and ACMG ratings on case annotations details (#344)
- Fixing problem with ACMD classifiction where VUS-3 was given but should be LB-2 (#359)
- Adding REST API for creating small variant queries (#332)
- Fixing beaconsite queries with dots in the key id (#369)
- Allowing joint queries of larger cohorts (#241)
- Documenting Clinical Beacon v1 protocol
- Improving performance for fetching result queries (#371)
- Capping max. number of cases to query at once (#372)
- Documenting release cycle and branch names
- Add extra annotations, i.e. additional variant scores to the filtered variants (#242)
- Fixing bug in project/cohort filter (#379)

### Full Change List

- Resolving problem with varfish-kiosk.
  - Auto-creating user `kiosk_user` when running in Kiosk mode.
  - Using custom middleware for kiosk user (#215).
- Kiosk annotation now uses `set -x` flag if `settings.DEBUG` is true.
- Mapping kiosk jobs to import queue.
- Fixing displaying of beacon information in results table.
- Fixing broken flags & comments popup for structural variants.
- Fixing broken search field.
- Extended manual for bug report workflow.
- Fixed recompute of variant stats of large small variant sets.
- Added index for `SmallVariant` model filtering for `case_id` and `set_id`. This may take a while!
- Allowing project owners and delegates to import cases via API (#207).
- Fix for broken link-out into MutationTaster (#240).
- Fixing SODAR Core template inconsistency (#150).
- Imports via API now are only allowed for projects of type `PROJECT` (#237).
- Fixing ensembl gene link-out to wrong genome build (#156).
- Added section for developers in manual (#267).
- Updating Clinvar export schema to the latest 1.7 version (#226).
- Migrated icons to iconify (#208).
- Bumped chrome-driver version (#208).
- Skipping codacy if token is not defined (#275).
- Adjusting models and UI for supporting GRCh38 annotated cases. It is currently not possible to migrate a GRCh37 case to GRCh38.
- Adjusting models and UI for supporting GRCh38 annotated cases. It is currently not possible to migrate a GRCh37 case to GRCh38.
- Setting `VARFISH_CADD_SUBMISSION_RELEASE` is called `VARFISH_CADD_SUBMISSION_VERSION` now (**breaking change**).
- `import_info.tsv` expected as in data release from `20210728` as built from varfish-db-downloader `1b03e97` or later.
- Extending columns of `Hgnc` to upstream update.
- Added feature to select multiple rows in results to create same annotation (#259)
- Added parameter to Docker entrypoint file to accept number of gunicorn workers
- Extended documentation for how to update specific tables (#177)
- Improving performance of project overview (#303)
- Improving performance of case listing (#304)
- Adding shortcut buttons to phenotype annotation (#289)
- Fixing issue with multiple added variants (#283)
- Make clinvar UI work with many annotations by making it load them lazily for one case at a time (#302)
- Implementing several usability improvements for clinvar submission editor (#286)
- Adding CI builds for Python 3.10 in Github actions, bumping numpy/pandas dependencies. Dropping support for Python 3.7.
- Fixing CADD annotation (#319)
- Adding mitochondrial inheritance to case phenotype annotation (#325)
- Fix issue with variant annotation export (#328)
- Adding REST API versioning (#333)
- Adding more postgres versions to CI (#337)
- Make migrations compatible with Postgres 14 (#338)
- DgvSvs and DgvGoldStandardSvs are two different data sources now
- Adding deep linking into case details tab (#344)
- Allowing direct update of variant annotations and ACMG ratings on case annotations details (#344)
- Removing [display\_hgmd\_public\_membership]{.title-ref} (#363)
- Fixing problem with ACMD classifiction where VUS-3 was given but should be LB-2 (#359)
- Adding REST API for creating small variant queries (#332)
- Upgrading sodar-core dependency to 0.10.10
- Fixing beaconsite queries with dots in the key id (#369)
- Allowing joint queries of larger cohorts (#241) This is achieved by performing fewer UNION queries (at most `VARFISH_QUERY_MAX_UNION=20` at one time)
- Documenting Clinical Beacon v1 protocol
- Improving performance for fetching result queries (#371)
- Fix to support sodar-core v0.10.10
- Capping max. number of cases to query at once (#372)
- Documenting release cycle and branch names
- Checking commit message trailers (#323)
- Add extra annotations to the filtered variants (#242)
- Fixing bug in project/cohort filter (#379)

## v0.23.9

### End-User Summary

- Bugfix release.

### Full Change List

- Fixing bugs that prevented properly running in production environment.

## v0.23.8

### End-User Summary

- Added SAML Login possibility from sodar-core to varfish
- Upgraded some icons and look and feel (via sodar-core).

### Full Change List

- Fixing bug that occured when variants were annotated earlier by the user with the variant disappering later on. This could be caused if the case is updated from singleton to trio later on.
- Added sso urls to config/urls.py
- Added SAML configuration to config/settings/base.py
- Added necessary tools to the Dockerfile
- Fix for missing PROJECTROLES\_DISABLE\_CATEGORIES variable in settings.
- Upgrading sodar-core dependency. This implies that we now require Python 3.7 or later.
- Upgrading various other packages including Django itself.
- Docker images are now published via ghcr.io.

## v0.23.7

**IMPORTANT**

This release contains a critical update. Prior to this release, all small and structural variant tables were marked as `UNLOGGED`. This was originally introduce to improve insert performance. However, it turned out that stability is greatly decreased. In the case of a PostgreSQL crash, these tables are emptied. This change should have been rolled back much earlier but that rollback was buggy. **This release now includes a working and verified fix.**

### End-User Summary

- Fixing stability issue with database schema.

### Full Change List

- Bump sodar-core to hotfix version. Fixes problem with remote permission synchronization.
- Adding migration to mark all `UNLOGGED` tables back to `LOGGED`. This should have been reverted earlier but because of a bug it did not.
- Fixing CI by calling `sudo apt-get update` once more.

## v0.23.6

### End-User Summary

- Fixing problem with remote permission synchronization.

### Full Change List

- Bump sodar-core to hotfix version. Fixes problem with remote permission synchronization.

## v0.23.5

### End-User Summary

- Adding back missing manual.
- Fixing undefined variable bug.
- Fixing result rows not colored anymore.
- Fixing double CSS import.

### Full Change List

- Fixing problem with `PROJECTROLES_ADMIN_OWNER` being set to `admin` default but the system user being `root` in the prebuilt databases. The value now defaults to `root`.
- Adding back missing manual in Docker image.
- Fixing problem with \"stopwords\" corpus of `nltk` not being present. This is now downloaded when building the Docker image.
- Fixing undefined variable bug.
- Fixing result rows not colored anymore.
- Fixing double CSS import.

## v0.23.4

### End-User Summary

- Fixing issue of database query in Clinvar Export feature where too large queries were created.
- Fixing search feature.

### Full Change List

- Docker image now includes commits to the next tag so the versioneer version display makes sense.
- Dockerfile entrypoint script uses timeout of 600s now for guniorn workers.
- Fixing issue of database query in Clinvar Export feature where too large queries were created and postgres ran out of stack memory.
- Adding more Sentry integrations (redis, celery, sqlalchemy).
- Fixing search feature.

## v0.23.3

### End-User Summary

- Bug fix release.

### Full Change List

- Bug fix release where the clinvar submission Vue.js app was not built.
- Fixing env file example for `SENTRY_DSN`.

## v0.23.2

### End-User Summary

- Bug fix release.

### Full Change List

- Bug fix release where Javascript was missing.

## v0.23.1

### End-User Summary

- Allowing to download all users annotation for whole project in one Excel/TSV file.
- Improving variant annotation overview per case/project and allowing download.
- Adding \"not hom. alt.\" filter setting.
- Allowing users to easily copy case UUID by icon in case heading.
- Fixing bug that made the user icon top right disappear.

### Full Change List

- Allowing to download all users annotation for whole project in one Excel/TSV file.
- Using SQL Alchemy query instrastructure for per-case/project annotation feature.
- Removing vendored JS/CSS, using CDN for development and download on Docker build instead.
- Adding \"not hom. alt.\" filter setting.
- Improving admin configuration documentation.
- Extending admin tuning documentation.
- Allowing users to easily copy case UUID by icon in case heading.
- Fixing bug that made the user icon top right disappear when beaconsite was disabled.
- Upgrade to sodar-core v0.9.1

## v0.23.0

### End-User Summary

- Fixed occasionally breaking tests `ProjectExportTest` by sorting member list. This bug didn\'t affect the correct output but wasn\'t consistent in the order of samples.
- Fixed above mentioned bug again by consolidating two distinct `Meta` classes in `Case` model.
- Fixed bug in SV tests that became visibly by above fix and created an additional variant that wasn\'t intended.
- Adapted core installation instructions in manual for latest data release and introduced use of VarFish API for import.
- Allowing (VarFish admins) to import regulatory maps. Users can use these maps when analyzing SVs.
- Adding \"padding\" field to SV filter form (regulatory tab).
- Celerybeat tasks in `variants` app are now executing again.
- Fixed `check_installation` management command. Index for `dbsnp` was missing.
- Bumped chromedriver version to 87.
- Fixed bug where file export was not possible when nubmer of resulting variants were \< 10.
- Fixed bug that made it impossible to properly sort by genotype in the results table.
- Cases can now be annotated with phenotypes and diseases. To speed up annotation, all phenotypes of all previous queries are listed for copy and paste. SODAR can also be queried for phenotypes.
- Properly sanitized output by Exomiser.
- Rebuild of variant summary database table happens every Sunday at 2:22am.
- Added celery queues `maintenance` and `export`.
- Adding support for connecting two sites via the GAGH Beacon protocol.
- Adding link-out to \"GenCC\".
- Adding \"submit to SPANR\" feature.

### Full Change List

- Fixed occasionally breaking tests `ProjectExportTest` by sorting member list. This bug didn\'t affect the correct output but wasn\'t consistent in the order of samples. Reason for this is unknown but might be that the order of cases a project is not always returned as in order they were created.
- Fixed above mentioned bug again by consolidating two distinct `Meta` classes in `Case` model.
- Fixed bug in SV tests that became visibly by above fix and created an additional variant that wasn\'t intended.
- Adapted core installation instructions in manual for latest data release and introduced use of VarFish API for import.
- Adding `regmaps` app for regulatory maps.
- Allowing users to specify padding for regulatory elements.
- Celerybeat tasks in `variants` app are now executing again. Issue was a wrong decorator.
- Fixed `check_installation` management command. Index for `dbsnp` was missing.
- Bumped chromedriver version to 87.
- Fixed bug where file export was not possible when number of resulting variants were \< 10.
- Fixed bug that made it impossible to properly sort by genotype in the results table.
- Adding tests for upstream sychronization backend code.
- Allowing users with the Contributor role to a project to annotate cases with phenotype and disease terms. They can obtain the phenotypes from all queries of all users for a case and also fetch them from SODAR.
- Adding files for building Docker images and documenting Docker (Compose) deployment.
- Properly sanitized output by Exomiser.
- Rebuild of variant summary database table happens every Sunday at 2:22am.
- Added celery queues `maintenance` and `export`.
- Adding support for connecting two sites via the GAGH Beacon protocol.
- Making CADD version behind CADD REST API configurable.
- Adding link-out to \"GenCC\".
- Adding \"submit to SPANR\" feature.

## v0.22.1

### End-User Summary

- Bumping chromedriver version.
- Fixed extra-annos import.

### Full Change List

- Bumping chromedriver version.
- Fixed extra-annos import.

## v0.22.0

### End-User Summary

- Fixed bug where some variant flags didn\'t color the row in filtering results after reloading the page.
- Fixed upload bug in VarFish Kiosk when vcf file was too small.
- Blocking upload of VCF files with GRCh38/hg38/hg19 builds for VarFish Kiosk.
- Support for displaying GATK-gCNV SVs.
- Tracking global maintenance jobs with background jobs and displaying them to super user.
- Adding \"Submit to CADD\" feature similar to \"Submit to MutationDistiller\".
- Increased default frequency setting of HelixMTdb max hom filter to 200 for strict and 400 for relaxed.
- It is now possible to delete ACMG ratings by clearing the form and saving it.
- Fixed bug when inheritance preset was wrongly selected when switching to `variant` in an index-only case.
- Added hemizygous counts filter option to frequency filter form.
- Added `synonymous` effect to be also selected when checking `all coding/deep intronic` preset.
- Saving uploads pre-checking in kiosk mode to facilitate debugging.
- Kiosk mode also accepts VCFs based on hg19.
- VariantValidator output now displays three-letter representation of AA.
- Documented new clinvar aggregation method and VarFish \"point rating\".
- Implemented new clinvar data display in variant detail.
- Added feature to assemble cohorts from cases spanning multiple projects and filter for them in a project-like query.
- Added column to results list indicating if a variant lies in a disease gene, i.e. a gene listed in OMIM.
- Displaying warning if priorization is not enabled when entering HPO terms.
- Added possibility to import \"extra annotations\" for display along with the variants.
- On sites deployed by BIH CUBI, we make the CADD, SpliceAI, MMSp, and dbscSNV scores available.
- In priorization mode, ORPHA and DECIPHER terms are now selectable.
- Fixed bug of wrong order when sorting by LOEUF score.
- Adding some UI documenation.
- Fixed bug where case alignment stats were not properly imported.
- Fixed bug where unfolding smallvariant details of a variant in a cohort that was not part of the base project caused a 404 error.
- Fixed bug that prevented case import from API.
- Increased speed of listing cases in case list view.
- Fixed bug that prevented export of project-wide filter results as XLS file.
- Adjusted genotype quality relaxed filter setting to 10.
- Added column with family name to results table of joint filtration.
- Added export of filter settings as JSON to structural variant filter form.
- Varseak Splicing link-out also considers refseq transcript.
- Fixed bug that occurred when sample statistics were available but sample was marked with having no genotype.
- Adjusted genotype quality strict filter setting to 10.
- Added possibility to export VCF file for cohorts.
- Increased logging during sample variant statistics computation.
- Using gnomAD exomes as initially selected frequency in results table.
- Using CADD as initially selected score metric in prioritization form.
- Fixed missing disease gene and mode of inheritance annotation in project/cohort filter results table.
- Catching errors during Kiosk annotation step properly.
- Fixed issues with file extension check in Kiosk mode during upload.
- \"1\" is now registered as heterozygous and homozygous state in genotype filter.
- Loading annotation and QC tabs in project cases list asyncronously.
- Increased timeout for VariantValidator response to 30 seconds.
- Digesting more VariantValidator responses.
- Fixed bug where when re-importing a case, the sample variants stats computation was performed on the member list of the old case. This could lead to the inconsistent state that when new members where added, the stats were not available for them. This lead to a 500 error when displaying the case overview page.
- Fixed missing QC plots in case detail view.
- Fixed bug in case VCF export where a variant existing twice in the results was breaking the export.
- Fixed log entries for file export when pathogenicity or phenotype scoring was activated.
- Bumped Chrome Driver version to 84 to be compatible with gitlab CI.
- CADD is now selected as default in pathogenicity scoring form (when available).
- Added global maintenance commands to clear old kiosk cases, inactive variant sets and expired exported files.
- Added `SvAnnotationReleaseInfo` model, information is filled during import and displayed in case detail view.
- Fixed bug that left number of small variants empty when they actually existed.
- Increased logging during case import.
- Marked old style import as deprecated.
- Fixed bug that prevented re-import of SVs.
- Fixed bug where a re-import of genotypes was not possible when the same variant types weren\'t present as in the initial import.
- Fixed bug where `imported` state of `CaseImportInfo` was already set after importing the first variant set.
- Integrated Genomics England PanelApp.
- Added command to check selected indexes and data types in database.
- Added columns to results table: `cDNA effect`, `protein effect`, `effect text`, `distance to splicesite`.
- Made effect columns and `distance to splicesite` column hide-able.
- Added warning to project/cohort query when a user tries to load previous results where not all variants are accessible.
- Renamed all occurrences of whitelist to allowlist and of blacklist to blocklist (sticking to what google introduced in their products).
- Fixed bug where cases were not deletable when using Chrome browser.
- Harmonized computation for relatedness in project-wide QC and in case QC (thus showing the same results if project only contains one family).
- Fixed failing case API re-import when user is not owner of previous import.
- Added `PROJECTROLES_EMAIL_` to config.
- Avoiding variants with asterisk alternative alleles.

### Full Change List

- Fixed bug where some variant flags didn\'t color the row in filtering results after reloading the page.
- Fixed upload bug in VarFish Kiosk when vcf file was too small and the file copy process didn\'t flush the file completely resulting in only a parly available header.
- Blocking upload of VCF files with GRCh38/hg38/hg19 builds for VarFish Kiosk.
- Bumping sodar-core dependency to v0.8.1.
- Using new sodar-core REST API infrastructure.
- Using sodar-core tokens app instead of local one.
- Support for displaying GATK-gCNV SVs.
- Fix of REST API-based import.
- Tracking global maintenance jobs with background jobs.
- Global background jobs are displayed with site plugin point via bgjobs.
- Bumping Chromedriver to make CI work.
- Adding \"Submit to CADD\" feature similar to \"Submit to MutationDistiller\".
- Increased default frequency setting of HelixMTdb max hom filter to 200 for strict and 400 for relaxed.
- It is now possible to delete ACMG ratings by clearing the form and saving it.
- Updated reference and contact information.
- File upload in Kiosk mode now checks for VCF file without samples.
- Fixed bug when inheritance preset was wrongly selected when switching to `variant` in an index-only case.
- Added hemizygous counts filter option to frequency filter form.
- Added `synonymous` effect to be also selected when checking `all coding/deep intronic` preset.
- Saving uploads pre-checking in kiosk mode to facilitate debugging.
- Kiosk mode also accepts VCFs based on hg19.
- VariantValidator output now displays three-letter representation of AA.
- Documented new clinvar aggregation method and VarFish \"point rating\".
- Implemented new clinvar data display in variant detail.
- Case/project overview allows to download all annotated variants as a file now.
- Querying for annotated variants on the case/project overview now uses the common query infrastructure.
- Updating plotly to v0.54.5 (displays message on missing WebGL).
- Added feature to assemble cohorts from cases spanning multiple projects and filter for them in a project-like query.
- Added column to results list indicating if a variant lies in a disease gene, i.e. a gene listed in OMIM.
- Displaying warning if priorization is not enabled when entering HPO terms.
- Added possibility to import \"extra annotations\" for display along with the variants.
- On sites deployed by BIH CUBI, we make the CADD, SpliceAI, MMSp, and dbscSNV scores available.
- In priorization mode, ORPHA and DECIPHER terms are now selectable.
- Fixed bug of wrong order when sorting by LOEUF score.
- Adding some UI documenation.
- Fixed bug where case alignment stats were not properly imported. Refactored case import in a sense that the new variant set gets activated when it is successfully imported.
- Fixed bug where unfolding smallvariant details of a variant in a cohort that was not part of the base project caused a 404 error.
- Fixed bug that prevented case import from API.
- Increased speed of listing cases in case list view.
- Fixed bug that prevented export of project-wide filter results as XLS file.
- Adjusted genotype quality relaxed filter setting to 10.
- Added column with family name to results table of joint filtration.
- Added export of filter settings as JSON to structural variant filter form.
- Varseak Splicing link-out also considers refseq transcript. This could lead to inconsistency when Varseak picked the wrong transcript to the HGVS information.
- Fixed bug that occurred when sample statistics were available but sample was marked with having no genotype.
- Adjusted genotype quality strict filter setting to 10.
- Added possibility to export VCF file for cohorts.
- Increased logging during sample variant statistics computation.
- Using gnomAD exomes as initially selected frequency in results table.
- Using CADD as initially selected score metric in prioritization form.
- Fixed missing disease gene and mode of inheritance annotation in project/cohort filter results table.
- Catching errors during Kiosk annotation step properly.
- Fixed issues with file extension check in Kiosk mode during upload.
- \"1\" is now registered as heterozygous and homozygous state in genotype filter.
- Loading annotation and QC tabs in project cases list asyncronously.
- Increased timeout for VariantValidator response to 30 seconds.
- Digesting more VariantValidator responses, namely `intergenic_variant_\d+` and `validation_warning_\d+`.
- Fixed bug where when re-importing a case, the sample variants stats computation was performed on the member list of the old case. This could lead to the inconsistent state that when new members where added, the stats were not available for them. This lead to a 500 error when displaying the case overview page.
- Fixed missing QC plots in case detail view.
- Fixed bug in case VCF export where a variant existing twice in the results was breaking the export.
- Fixed log entries for file export when pathogenicity or phenotype scoring was activated. The variants are sorted by score in this case which led to messy logging which was designed for logging when the chromosome changes.
- Bumped Chrome Driver version to 84 to be compatible with gitlab CI.
- CADD is now selected as default in pathogenicity scoring form (when available).
- Added global maintenance commands to clear old kiosk cases, inactive variant sets and expired exported files.
- Added `SvAnnotationReleaseInfo` model, information is filled during import and displayed in case detail view.
- Fixed bug that left number of small variants empty when they actually existed. This happened when SNVs and SVs were imported at the same time.
- Increased logging during case import.
- Marked old style import as deprecated.
- Fixed bug that prevented re-import of SVs by altering the unique constraint on the `StructuralVariant` table.
- Fixed bug where a re-import of genotypes was not possible when the same variant types weren\'t present as in the initial import. This was done by adding a `state` field to the `VariantSetImportInfo` model.
- Fixed bug where `imported` state of `CaseImportInfo` was already set after importing the first variant set.
- Integrated Genomics England PanelApp via their API.
- Added command to check selected indexes and data types in database.
- Added columns to results table: `cDNA effect`, `protein effect`, `effect text`, `distance to splicesite`.
- Made effect columns and `distance to splicesite` column hide-able.
- Added warning to project/cohort query when a user tries to load previous results where not all variants are accessible.
- Renamed all occurrences of whitelist to allowlist and of blacklist to blocklist (sticking to what google introduced in their products).
- Fixed bug where cases were not deletable when using Chrome browser.
- Harmonized computation for relatedness in project-wide QC and in case QC (thus showing the same results if project only contains one family).
- Fixed failing case API re-import when user is not owner of previous import. Now also all users with access to the project (except guests) can list the cases.
- Added `PROJECTROLES_EMAIL_` to config.
- Avoiding variants with asterisk alternative alleles.

## v0.21.0

### End-User Summary

- Added preset for mitochondrial filter settings.
- Fixed bug where HPO name wasn\'t displayed in textarea after reloading page.
- Added possibility to enter OMIM terms in phenotype prioritization filter.
- Added maximal exon distance field to `Variants & Effects` tab.
- Adapted `HelixMTdb` filter settings, allowing to differntiate between hetero- and homoplasmy counts.
- Increased default max collective background count in SV filter from 0 to 5.
- Included lists of genomic regions, black and white genelists and reworked HPO list in table header as response for what was filtered for (if set).
- Added `molecular` assessment flag for variant classification.
- Fixed bug where activated mitochondrial frequency filter didn\'t include variants that had no frequency database entry.
- Added inheritance preset and quick preset for X recessive filter.
- Removed VariantValidator link-out.
- Now smallvariant comments, flags and ACMG are updating in the smallvariant details once submitted.
- Deleting a case (only possible as root) runs now as background job.
- Fixed bug in compound heterozygous filter with parents in pedigree but without genotype that resulted in variants in genes that didn\'t match the pattern.
- Bumped django version to 1.11.28 and sodar core version to bug fix commit.
- Fixed bug where structural variant results were not displayed anymore after introduced `molecular` assessment flag.
- Fixed bug where variant comments and flags popup was not shown in structural variant results after updating smallvariant details on the fly.
- Made `Download as File` and `Submit to MutationDistiller` buttons more promiment.
- Adapted preset settings for `ClinVar Pathogenic` setting.
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
- Added more documentation throughout the UI.
- Added option to toggle displaying of logs during filtration, by default they are hidden.
- Fixed broken displaying of inhouse frequencies in variant detail view.
- Added variant annotation list (comments, flags, ACMG ratings) to project-wide info page.
- Row in filter results now turns gray when any flag is set (except bookmark flag; summary flag still colours in other colour).
- Fixed bug where comments and flags in variant details weren\'t updated when the variant details have been opened before.
- Added QC TSV download and per-sample metrics table to projec-wide QC.
- Removed ExAC locus link in result list, added gnomAD link to gene.
- Catching connection exceptions during file export with enabled pathogenicity and/or phenotype scoring.
- Fixed project/case search that delivered search results for projects that the searching user had no access to (only search was affected, access was not granted).
- Made case comments count change in real time.

### Full Change List

- Added preset for mitochondrial filter settings.
- Fixed bug where HPO name wasn\'t displayed in textarea after reloading page. HPO terms are now also checked for validity in textbox on the fly.
- Added possibility to enter OMIM terms in phenotype prioritization filter. The same textbox as for HPO terms also accepts OMIM terms now.
- Added maximal exon distance field to `Variants & Effects` tab.
- (Hopefully) fixing importer bug (#524).
- Adapted `HelixMTdb` filter settings, allowing to differntiate between hetero- and homoplasmy counts.
- Fixed inactive filter button to switch from SV filter to small variant filter.
- Increased default max collective background count in SV filter from 0 to 5.
- Included lists of genomic regions, black and white genelists and reworked HPO list in table header as response for what was filtered for (if set).
- Added `molecular` assessment flag for variant classification.
- Fixed bug where activated mitochondrial frequency filter didn\'t include variants that had no frequency database entry.
- Added inheritance preset and quick preset for X recessive filter.
- Removed VariantValidator link-out.
- Now smallvariant comments, flags and ACMG are updating in the smallvariant details once submitted.
- Deleting a case (only possible as root) runs now as background job.
- Fixed bug in compound heterozygous filter with parents in pedigree but without genotype that resulted in variants in genes that didn\'t match the pattern.
- Bumped django version to 1.11.28 and sodar core version to bug fix commit.
- Fixed bug where structural variant results were not displayed anymore after introduced `molecular` assessment flag.
- Fixed bug where variant comments and flags popup was not shown in structural variant results after updating smallvariant details on the fly.
- Made `Download as File` and `Submit to MutationDistiller` buttons more promiment.
- Adapted preset settings for `ClinVar Pathogenic` setting.
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
- Added more documentation throughout the UI.
- Added option to toggle displaying of logs during filtration, by default they are hidden.
- Fixed broken displaying of inhouse frequencies in variant detail view.
- Added variant annotation list (comments, flags, ACMG ratings) to project-wide info page.
- Row in filter results now turns gray when any flag is set (except bookmark flag; summary flag still colours in other colour).
- Fixed bug where comments and flags in variant details weren\'t updated when the variant details have been opened before.
- Added QC TSV download and per-sample metrics table to projec-wide QC.
- Removed ExAC locus link in result list, added gnomAD link to gene.
- Catching connection exceptions during file export with enabled pathogenicity and/or phenotype scoring.
- Fixed project/case search that delivered search results for projects that the searching user had no access to (only search was affected, access was not granted).
- Made case comments count change in real time.

## v0.20.0

### End-User Summary

- Added count of annotations to case detail view in `Variant Annotation` tab.
- De-novo quick preset now selects `AA change, splicing (default)` for sub-preset `Impact`, instead of `all coding, deep intronic`.
- Added project-wide option to disable pedigree sex check.
- Added button to case detail and case list to fix sex errors in pedigree for case or project-wide.
- Added command `import_cases_bulk` for case bulk import, reading arguments from a JSON file.
- Entering and suggeting HPO terms now requires at least 3 typed charaters.
- Fixed broken variant details page when an HPO id had no matching HPO name.
- Fixed bug in joint filtration filter view where previous genomic regions where not properly restored in the form.
- Fixed bug that lead to an AJAX error in the filter view when previous filter results failed to load because the variants of a case were deleted in the meantime.
- Entering the filter view is now only possible when there are variants and a variant set. When there are variant reported but no variant set, a warning in form of a small red icon next to the number of variants is displayed, complaining about an inconsistent state.
- In case of errors, you can now give feedback in a form via Sentry.
- Fixed bug that occurred during project file export and MutationTaster pathogenicity scoring and a variant was multiple times in the query string for mutation taster.
- Adding REST API for Cases.
- Adding site app for API token management.
- Added frequency databases for mitochondrial chromosome, providing frequency information in the small variant details.
- Fixed periodic tasks (contained clean-up jobs) and fixed tests for periodic tasks.
- Adding REST API for Cases and uploading cases.
- Adding GA4GH beacon button to variant list row and details. Note that this must be activated in the user profile settings.
- Added filter support to queries and to filter form for mitochondrial genome.

### Full Change List

- Added count of annotations to case detail view in `Variant Annotation` tab.
- De-novo quick preset now selects `AA change, splicing (default)` for sub-preset `Impact`, instead of `all coding, deep intronic`.
- Added project-wide option to disable pedigree sex check.
- Added button to case detail and case list to fix sex errors in pedigree for case or project-wide.
- Added command `import_cases_bulk` for case bulk import, reading arguments from a JSON file.
- Entering and suggeting HPO terms now requires at least 3 typed charaters. Also only sending the query if the HPO term string changed to reduce number of executed database queries.
- Fixed broken variant details page when an HPO id had no matching HPO name. This happened when gathering HPO names, retrieving HPO id from `Hpo` database given the OMIM id and then the name from `HpoName`. The databases `Hpo` and `HpoName` don\'t match necessarly via `hpo_id`, in this case because of an obsolete HPO id `HP:0031988`. Now reporting `"unknown"` for the name instead of `None` which broke the sorting routine.
- Fixed bug in `ProjectCasesFilterView` where previous genomic regions where not properly restored in the form.
- Fixed bug that lead to an AJAX error in the filter view when previous filter results failed to load because the variants of a case were deleted in the meantime.
- Entering the filter view is now only possible when there are variants and a variant set. When there are variant reported but no variant set, a warning in form of a small red icon next to the number of variants is displayed, complaining about an inconsistent state.
- Using latest sentry SDK client.
- Fixed bug that occurred during project file export and MutationTaster pathogenicity scoring and a variant was multiple times in the query string for mutation taster.
- Adding REST API for Cases.
- Copying over token management app from Digestiflow.
- Added frequency databases `mtDB`, `HelixMTdb` and `MITOMAP` for mitochondrial chromosome. Frequency information is provided in the small variant detail view.
- Fixed periodic tasks (contained clean-up jobs) and fixed tests for periodic tasks.
- Adding REST API for `Case`.
- Extending `importer` app with API to upload annotated TSV files and models to support this.
- Adding GA4GH beacon button to variant list row and details. Note that this must be activated in the user profile settings.
- Added filter support to queries and to filter form for mitochondrial genome.

## v0.19.0

### End-User Summary

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
- Added `django_su` to allow superusers to temporarily take on the identity of another user.
- Fixed bug in which some variants in comphet mode only had one variant in results list.
- Added user-definable, project-specific tags to be attached to a case. Enter them in the project settings, use them in the case details page.
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
- Fixed UI bug when selecting `ClinVar only` as flags.
- Added link-out to variant when present in ClinVar.
- Fixed broken SV filter button in smallvariant filter form.
- Added link-out to case from import bg job detail page.
- Added `recessive` quick presets setting.
- Added functionality to delete small variants and structural variants of a case separately.
- Fixed bug in which deleting a case didn\'t delete the sodar core background jobs.
- Old variants stats data is not displayed anymore in case QC overview when case is re-imported.

### Full Change List

- Added inhouse frequency information to variant detail page.
- Added link-out in locus dropdown menu in results table to VariantValidator. To be able to construct the link, `refseq_hgvs_c` and `refseq_transcript_id` are also exported in query.
- Added filter-by-status dropdown menu to case overview page. With this, the bootstrap addon `bootstrap-select` was added to the static folder.
- Added link-out to pubmed in NCBI gene RIF list in variant details view. For this, `NcbiGeneRif` table was extended with a `pubmed_ids` field.
- Fixing syncing project with upstream SODAR project.
- Added controls to gnomad genomes and gnomad exomes frequencies in the database table by extending the fields. Added controls to frequency table in variant details view.
- Improving HiPhive integration:
  - Adding human, human/mouse similarity search.
  - Using POST request to Exomiser to increase maximal number of genes.
- Replacing old global presets with one preset per filter category.
- Using ISA-tab for syncing with upstream project.
- Added recessive, homozygous recessive and denovo filter to genotype settings. Homozygous recessive and denovo filter are JS code re-setting values in dropdown boxes. Recessive filter behaves as comp het filter UI-wise, but joins results of both homozygous and compound heterozygous filter internally.
- Entering HPO terms received a typeahead feature and the input is organized in tags/badges.
- Import of background database now less memory intensive by disabling autovacuum option during import and removing atomic transactions. Instead, tables are emptied by genome release in case of failure in import.
- Added project-wide alignment statistics.
- Added `django_su` to allow superusers to temporarily take on the identity of another user.
- Fixed bug in which some variants in comphet mode only had one variant in results list. The hgmd query was able to create multiple entries for one variant which was reduced to one entry in the resulting list. To correct for that, the range query was fixed and the grouping in the lateral join was removed.
- Added user-definable, project-specific tags to be attached to a case.
- Added alert fields for all ajax calls.
- Removed javascript error when pre-loaded HPO terms were decorated into tags.
- Removed (non function-disturbing) javascript error when pre-loaded HPO terms were decorated into tags.
- Fixed coloring of rows when flags have been set. When summary is not set but other flags, the row is colored in gray to represent a WIP state. Coloring happens now immediately and not only when page is re-loaded.
- Fixed dominant/denovo genotype preset.
- Minor adjustments/renamings to presets.
- Link-out to genomics england panelapp.
- Fixed partly broken error decoration on hidden tabs on field input errors.
- Introduced bigint fields into postgres sequences counter for smallvariant, smallvariantquery\_query\_results and projectcasessmallvariantquery\_query\_results tables.
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
- Fixed UI bug when selecting `ClinVar only` as flags.
- Added link-out to variant when present in ClinVar by adding the SCV field from the HGNC database to the query.
- Fixed broken SV filter button in smallvariant filter form.
- Added link-out to case from import bg job detail page.
- Added `recessive` quick presets setting.
- Added functionality to delete small variants and structural variants of a case separately.
- Fixed bug in which deleting a case didn\'t delete the sodar core background jobs.
- Old variants stats data is not displayed anymore in case QC overview when case is re-imported.

## v0.18.0

### End-User Summary

- Added caching for pathogenicity scores api results.
- Added column to the project wide filter results table that displays the number of affected cases per gene.
- Enabled pathogenicity scoring for project-wide filtration.
- Added LOEUF gnomAD constraint column to results table.
- Added link-out to MetaDome in results table.

### Full Change List

- Added new database tables `CaddPathogenicityScoreCache`, `UmdPathogenicityScoreCache`, `MutationtasterPathogenicityScoreCache` to cache pathogenicity scores api results.
- Added column to the project wide filter results table that displays the number of affected cases per gene. I.e. the cases (not samples) that have a variant in a gene are counted and reported.
- Enabled pathogenicity scoring for project-wide filtration. This introduced a new table `ProjectCasesSmallVariantQueryVariantScores` to store the scoring results for a query.
- Added LOEUF gnomAD constraint column to results table.
- Added link-out to MetaDome in results table.
