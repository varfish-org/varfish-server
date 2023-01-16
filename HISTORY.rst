===================
History / Changelog
===================

------------------------------
HEAD (unreleased; bollonaster)
------------------------------

End-User Summary
================

- Starting with development of Bollonaster (VarFish v2)
- Documenting problem with extra annotations in ``20210728` data release (#450).
  Includes instructions on how to apply patch to get ``20210728b``.
- Add Transcripts GnomadAD constraints and clinvar reports in the export(#568)
- Extra annotations in export completed and tested (#495).
- Removing problematic username modification behaviour on login page (#459).
- Displaying login page text from settings again (#458).
- Suppress "submit to CADD" and "submit to SPANR" buttons for multi-case form (#478).
  This has not been implemented so far.
- Fixing paths in "Variant Ingest" documentation (#472).
- Small extension of "Resolution proposal" template (#472).
- Adjusting wrong release name to "anthenea" (#479).
- Adding "show all variant carriers" feature (#470).
- Properly display the clinvar annotations that we have in the database (#464).
- Adjusting default frequency filters for "clinvar pathogenic" filter: remove all threshold (#464).
- Adding note about difference with upstream Clinvar (#464).
- Switching scoring to MutationTaster 85 interface, added back MT 85 link-out alongside MT 2021 link-out (#509).
- Made flag filter and flag form nomenclature consistent (#297).
- Improved developer setup documentation and added Windows installation instructions (#533).
- Fixed broken VariantValidator query (#523).
- Fixed smallvariant flags filter query (#502).
- Added flags ``segregates``, ``doesnt_segregate`` and ``no_disease_association`` to file export (#502).
- Adjusting path to new varfish-annotator db download (#546).
- Adding feature to enable and configure link-out to HGMD (#576).
- Small variant filtration results now allow to easily look up second hits in the same gene (#573).
- Structural filtration results now allow to easily look up second hits in the same gene (#574).
- Fixed bug where Exac and thousand genomes settings were not shown in frequency tab for GRCh37 (#597).
- Form template reports error if genomebuild variable is not set (#607).
- The StructuralVariant model is augmented (#566).
  This adds capability to properly represent break-end (BND) records.
  Also, per--genotype type counts are added.
  A full re-import after re-annotation with varfish-annotator v0.23 or above is recommended.
  Alternatively, you can use ``python manage.py svs_sv_fill_nulls`` to update the records on the fly.
- Implement new in-house background database for structural variants (#32).
- Allow to exclude cases from in-house database through project settings (#579).
- Adding distinct de novo genotype setting (#562).
- Adding section presets for SV filtration (#616).
- Adjusting SV filtration presets (#616).
- Fix bug with thousand genomes frequencies in SV filtration (#619).
- Displaying disease gene icon also for SVs (#620).
- Fix bug with gene constraint display for intergenic variants (#620).
- De novo quick preset now uses strict quality (#624).
- Create single result row even if multiple clinvar entries (#565).
- Fixing clinvar filter (#296).
  **This will require an import of the updated Clinvar ``20210728c`` data (#296).**
- Improving Clinvar filter performance (#635).
- Warning in the case of truncated displayed results (#641).
- Improving Clinvar record aggregation (#640).
- Fixing ClinVar submission XML generation (#677).
- Fixing ClinVar export editor timing issues (#667, #668).
- Fixing hemizygous count display in fold-outs (#646).
- Fixing clinvar submission sex/gender update (#686).
- Fixing issue with phenotype name in Clinvar (#689).
- Initial vue.js implementation for small variant filtration (#563).
- Changing ClinVar link-out to VCV entry instead of coordinates (#693).
- Adding support to create custom gene panels (#723).
- Allow operators to upload per-gene annotations to cases (#575) on import.
- Display warning icon in filter results table if non-selected frequency is high (#708).
- Fix query schema (#749).
- Migrating case list and details to Vue.js (#743).
- Fix bug in SV background database building (#757).
- Allowing to read clinvar submission reports (#759).
- Fix bug in filtration form with max. exon dist (#753).
- Allow display of extra annos in Vue.js filtration (#755).
- Fix variant icon display (#745).
- Improving installation instructions (#735).
- Implementing case-independent variant annotations (#747).
- Fixing bug in mutationtaster integration (#790).
- Fixing bug in Vue.js filtration without prior query (#794).
- Fixing bug in SV background database generation (#792).
- Gene prioritization using CADA (Case Annotations and Disorder Annotations) scores (#596)

Full Change List
================

- Starting with development of Bollonaster (VarFish v2)
- Documenting problem with extra annotations in ``20210728` data release (#450).
  Includes instructions on how to apply patch to get ``20210728b``.
- Removing problematic username modification behaviour on login page (#459).
- Displaying login page text from settings again (#458).
- Suppress "submit to CADD" and "submit to SPANR" buttons for multi-case form (#478).
  This has not been implemented so far.
- Fixing paths in "Variant Ingest" documentation (#472).
- Small extension of "Resolution proposal" template (#472).
- Adjusting wrong release name to "anthenea" (#479).
- Adding "show all variant carriers" feature (#470).
- Properly display the clinvar annotations that we have in the database (#464).
- Adjusting default frequency filters for "clinvar pathogenic" filter: remove all threshold (#464).
- Adding note about difference with upstream Clinvar (#464).
- Switching scoring to MutationTaster 85 interface, added back MT 85 link-out alongside MT 2021 link-out (#509).
- CADD setup fix for documentation (#520)
- Made flag filter and flag form nomenclature consistent (#297).
- Updating ``utility/*.sh`` scripts from "upstream" sodar-server (#531).
- Improved developer setup documentation and added Windows installation instructions (#533).
- Skip commit trailer checks for dependabot (#537).
- Fixed broken VariantValidator query (#523).
- Converted not cooperative tooltip to standard title on Filter & Display button (#508).
- Fixed smallvariant flags filter query (#502).
- Added flags ``segregates``, ``doesnt_segregate`` and ``no_disease_association`` to file export (#502).
- Adjusting path to new varfish-annotator db download (#546).
- Fixing issue with sync-from-remote when no remote is defined (#570).
- Adding feature to enable and configure link-out to HGMD (#576).
- Small variant filtration results now allow to easily look up second hits in the same gene (#573).
- Structural filtration results now allow to easily look up second hits in the same gene (#574).
- Bugfix broken SV filter (#587).
- Fixed bug where Exac and thousand genomes settings were not shown in frequency tab for GRCh37 (#597).
- Form template reports error if genomebuild variable is not set (#607).
- Making ``keyvalue`` more robust to failure (#613).
- Implement new in-house background database for structural variants (#32).
- Allow to exclude cases from in-house database through project settings (#579).
- Adding distinct de novo genotype setting (#562).
- Adding section presets for SV filtration (#616).
- Adjusting SV filtration presets (#616).
- Fix bug with thousand genomes frequencies in SV filtration (#619).
- Displaying disease gene icon also for SVs (#620).
- Fix bug with gene constraint display for intergenic variants (#620).
- Fix import bug in import_tables.py (#625).
- De novo quick preset now uses strict quality (#624).
- Create single result row even if multiple clinvar entries (#565).
- Fixing clinvar filter (#296).
  **This will require an import of the updated Clinvar ``20210728c`` data (#296).**
- Improving Clinvar filter performance (#635).
  Database indices were missing, assumedly because of a Django ``makemigrations`` bug.
- Warning in the case of truncated displayed results (#641).
- Improving Clinvar record aggregation (#640).
- Fixing Docker builds (#660).
- Fixing ClinVar submission XML generation (#677).
- Adding regular task to sync ClinVar submission ``Individual`` sex from the one from the ``Case``.
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

------
v1.2.0
------

This is the first stable VarFish Server release.
It is the same as v1.1.4.

------
v1.1.4
------

End-User Summary
================

Full Change List
================

- Installing same postgres version as in docker-compose server (12).

------
v1.1.3
------

End-User Summary
================

- Fixing problem with import info display for non-superusers (#431)
- Schema and documentation for case QC info (#428)
- Adding support for HGNC IDs in gene allow lists (#432)
- PanelApp will now populate the gene allow list with HGNC gene IDs (#432)

Full Change List
================

- Fixing problem with import info display for non-superusers (#431)
- Schema and documentation for case QC info (#428)
- Adding support for HGNC IDs in gene allow lists (#432)
- PanelApp will now populate the gene allow list with HGNC gene IDs (#432)
- Adding ``pg_dump`` admin command and documentation (#430)

------
v1.1.2
------

End-User Summary
================

- Fixing bug in XLSX export (#417)
- Fixing problem with multi-sample queries (#419)
- Fixing issue with cohort queries (#420)
- Fixing issue with mutationtaster queries (#423)
- Fixing problem with multi-variant update (#419)

Full Change List
================

- Fixing bug in corner case of multi variant annotation (#412)
- Updating documentation for v1 release (#410)
- Fixing issue with ``fa-solid:refresh`` icon (#409)
- Fixing page titles (#409)
- Fixing bug in XLSX export (#417)
- Fixing problem with multi-sample queries (#419).
  This is done by rolling back adding the ``_ClosingWrapper`` class.
  We will need a different approach for the queries than was previously attempted here.
- Fixing issue with cohort queries (#420)
- Fixing issue with mutationtaster queries (#423)
- Fixing problem with multi-variant update (#419)

------
v1.1.1
------

This is the first release candidate of the VarFish "Anthenea" release (v1).
Importantly, the first stable release for v1 will be v1.2.0 (see `Release Cycle Documentation <https://varfish-server.readthedocs.io/en/latest/release_cycle.html>`__ for a full explanation of version semantics).

This release adds some more indices so the migrations might take some more time.

End-User Summary
================

- Fixing problem with CNV import (#386)
- Fixing problem with user annotation of nonexistent variants (#404)

Full Change List
================

- Adding REST API for generating query shortcuts (#367)
- Filter queries in REST API to selected case and not all by user
- Fixing problem with CNV import (#386)
- Adding index to improve beaconsite performance (#389)
- Adding missing ``mdi`` iconset (#284)
- Strip trailing slashes in beconsite entrypoints (#388)
- Documenting PAP setup (#393)
- Adding more indices (#395)
- Fixing discrepancy with REST API query shortcuts (#402)

------
v1.1.0
------

This is the first release candidate of the VarFish "Anthenea" release (v1).
Importantly, the first stable release for v1 will be v1.2.0 (see `Release Cycle Documentation <https://varfish-server.readthedocs.io/en/latest/release_cycle.html>`__ for a full explanation of version semantics).

Breaking changes, see below.

End-User Summary
================

- Fixing Kiosk mode of VarFish.
- Fixing displaying of beacon information in results table.
- Fixing broken flags & comments popup for structural variants.
- Fixing broken search field.
- Extended manual for bug report workflow.
- Fixed recompute of variant stats of large small variant sets.
- Added index for ``SmallVariant`` model filtering for ``case_id`` and ``set_id``.
  This may take a while!
- Allowing project owners and delegates to import cases via API (#207).
- Fix for broken link-out into MutationTaster (#240).
- Fixing SODAR Core template inconsistency (#150).
- Imports via API now are only allowed for projects of type ``PROJECT`` (#237).
- Fixing ensembl gene link-out to wrong genome build (#156).
- Added section for developers in manual (#267).
- Updating Clinvar export schema to 1.7 version (#226).
- Migrated icons to iconify (#208).
- Bumped chrome-driver version (#208).
- VarFish now allows for the import of GRCh38 annotated variants.
  For this, GRCh38 background data must be imported.
  Kiosk mode does not support GRCh38 yet.
  **This is a breaking change, new data and CLI must be used!**
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

Full Change List
================

- Resolving problem with varfish-kiosk.
    - Auto-creating user ``kiosk_user`` when running in Kiosk mode.
    - Using custom middleware for kiosk user (#215).
- Kiosk annotation now uses ``set -x`` flag if ``settings.DEBUG`` is true.
- Mapping kiosk jobs to import queue.
- Fixing displaying of beacon information in results table.
- Fixing broken flags & comments popup for structural variants.
- Fixing broken search field.
- Extended manual for bug report workflow.
- Fixed recompute of variant stats of large small variant sets.
- Added index for ``SmallVariant`` model filtering for ``case_id`` and ``set_id``.
  This may take a while!
- Allowing project owners and delegates to import cases via API (#207).
- Fix for broken link-out into MutationTaster (#240).
- Fixing SODAR Core template inconsistency (#150).
- Imports via API now are only allowed for projects of type ``PROJECT`` (#237).
- Fixing ensembl gene link-out to wrong genome build (#156).
- Added section for developers in manual (#267).
- Updating Clinvar export schema to the latest 1.7 version (#226).
- Migrated icons to iconify (#208).
- Bumped chrome-driver version (#208).
- Skipping codacy if token is not defined (#275).
- Adjusting models and UI for supporting GRCh38 annotated cases.
  It is currently not possible to migrate a GRCh37 case to GRCh38.
- Adjusting models and UI for supporting GRCh38 annotated cases.
  It is currently not possible to migrate a GRCh37 case to GRCh38.
- Setting ``VARFISH_CADD_SUBMISSION_RELEASE`` is called ``VARFISH_CADD_SUBMISSION_VERSION`` now (**breaking change**).
- ``import_info.tsv`` expected as in data release from ``20210728`` as built from varfish-db-downloader ``1b03e97`` or later.
- Extending  columns of ``Hgnc`` to upstream update.
- Added feature to select multiple rows in results to create same annotation (#259)
- Added parameter to Docker entrypoint file to accept number of gunicorn workers
- Extended documentation for how to update specific tables (#177)
- Improving performance of project overview (#303)
- Improving performance of case listing (#304)
- Adding shortcut buttons to phenotype annotation (#289)
- Fixing issue with multiple added variants (#283)
- Make clinvar UI work with many annotations by making it load them lazily for one case at a time (#302)
- Implementing several usability improvements for clinvar submission editor (#286)
- Adding CI builds for Python 3.10 in Github actions, bumping numpy/pandas dependencies.
  Dropping support for Python 3.7.
- Fixing CADD annotation (#319)
- Adding mitochondrial inheritance to case phenotype annotation (#325)
- Fix issue with variant annotation export (#328)
- Adding REST API versioning (#333)
- Adding more postgres versions to CI (#337)
- Make migrations compatible with Postgres 14 (#338)
- DgvSvs and DgvGoldStandardSvs are two different data sources now
- Adding deep linking into case details tab (#344)
- Allowing direct update of variant annotations and ACMG ratings on case annotations details (#344)
- Removing `display_hgmd_public_membership` (#363)
- Fixing problem with ACMD classifiction where VUS-3 was given but should be LB-2 (#359)
- Adding REST API for creating small variant queries (#332)
- Upgrading sodar-core dependency to 0.10.10
- Fixing beaconsite queries with dots in the key id (#369)
- Allowing joint queries of larger cohorts (#241)
  This is achieved by performing fewer UNION queries (at most ``VARFISH_QUERY_MAX_UNION=20`` at one time)
- Documenting Clinical Beacon v1 protocol
- Improving performance for fetching result queries (#371)
- Fix to support sodar-core v0.10.10
- Capping max. number of cases to query at once (#372)
- Documenting release cycle and branch names
- Checking commit message trailers (#323)
- Add extra annotations to the filtered variants (#242)
- Fixing bug in project/cohort filter (#379)

-------
v0.23.9
-------

End-User Summary
================

- Bugfix release.

Full Change List
================

- Fixing bugs that prevented properly running in production environment.

-------
v0.23.8
-------

End-User Summary
================

- Added SAML Login possibility from sodar-core to varfish
- Upgraded some icons and look and feel (via sodar-core).

Full Change List
================

- Fixing bug that occured when variants were annotated earlier by the user with the variant disappering later on.
  This could be caused if the case is updated from singleton to trio later on.
- Added sso urls to config/urls.py
- Added SAML configuration to config/settings/base.py
- Added necessary tools to the Dockerfile
- Fix for missing PROJECTROLES_DISABLE_CATEGORIES variable in settings.
- Upgrading sodar-core dependency.
  This implies that we now require Python 3.7 or later.
- Upgrading various other packages including Django itself.
- Docker images are now published via ghcr.io.

-------
v0.23.7
-------

**IMPORTANT**

This release contains a critical update.
Prior to this release, all small and structural variant tables were marked as ``UNLOGGED``.
This was originally introduce to improve insert performance.
However, it turned out that stability is greatly decreased.
In the case of a PostgreSQL crash, these tables are emptied.
This change should have been rolled back much earlier but that rollback was buggy.
**This release now includes a working and verified fix.**

End-User Summary
================

- Fixing stability issue with database schema.

Full Change List
================

- Bump sodar-core to hotfix version.
  Fixes problem with remote permission synchronization.
- Adding migration to mark all ``UNLOGGED`` tables back to ``LOGGED``.
  This should have been reverted earlier but because of a bug it did not.
- Fixing CI by calling ``sudo apt-get update`` once more.

-------
v0.23.6
-------

End-User Summary
================

- Fixing problem with remote permission synchronization.

Full Change List
================

- Bump sodar-core to hotfix version.
  Fixes problem with remote permission synchronization.

-------
v0.23.5
-------

End-User Summary
================

- Adding back missing manual.
- Fixing undefined variable bug.
- Fixing result rows not colored anymore.
- Fixing double CSS import.

Full Change List
================

- Fixing problem with ``PROJECTROLES_ADMIN_OWNER`` being set to ``admin`` default but the system user being ``root`` in the prebuilt databases.
  The value now defaults to ``root``.
- Adding back missing manual in Docker image.
- Fixing problem with "stopwords" corpus of ``nltk`` not being present.
  This is now downloaded when building the Docker image.
- Fixing undefined variable bug.
- Fixing result rows not colored anymore.
- Fixing double CSS import.

-------
v0.23.4
-------

End-User Summary
================

- Fixing issue of database query in Clinvar Export feature where too large queries were created.
- Fixing search feature.

Full Change List
================

- Docker image now includes commits to the next tag so the versioneer version display makes sense.
- Dockerfile entrypoint script uses timeout of 600s now for guniorn workers.
- Fixing issue of database query in Clinvar Export feature where too large queries were created and postgres ran out of stack memory.
- Adding more Sentry integrations (redis, celery, sqlalchemy).
- Fixing search feature.

-------
v0.23.3
-------

End-User Summary
================

- Bug fix release.

Full Change List
================

- Bug fix release where the clinvar submission Vue.js app was not built.
- Fixing env file example for ``SENTRY_DSN``.

-------
v0.23.2
-------

End-User Summary
================

- Bug fix release.

Full Change List
================

- Bug fix release where Javascript was missing.

-------
v0.23.1
-------

End-User Summary
================

- Allowing to download all users annotation for whole project in one Excel/TSV file.
- Improving variant annotation overview per case/project and allowing download.
- Adding "not hom. alt." filter setting.
- Allowing users to easily copy case UUID by icon in case heading.
- Fixing bug that made the user icon top right disappear.

Full Change List
================

- Allowing to download all users annotation for whole project in one Excel/TSV file.
- Using SQL Alchemy query instrastructure for per-case/project annotation feature.
- Removing vendored JS/CSS, using CDN for development and download on Docker build instead.
- Adding "not hom. alt." filter setting.
- Improving admin configuration documentation.
- Extending admin tuning documentation.
- Allowing users to easily copy case UUID by icon in case heading.
- Fixing bug that made the user icon top right disappear when beaconsite was disabled.
- Upgrade to sodar-core v0.9.1

-------
v0.23.0
-------

End-User Summary
================

- Fixed occasionally breaking tests ``ProjectExportTest`` by sorting member list.
  This bug didn't affect the correct output but wasn't consistent in the order of samples.
- Fixed above mentioned bug again by consolidating two distinct ``Meta`` classes in ``Case`` model.
- Fixed bug in SV tests that became visibly by above fix and created an additional variant that wasn't intended.
- Adapted core installation instructions in manual for latest data release and introduced use of VarFish API for import.
- Allowing (VarFish admins) to import regulatory maps.
  Users can use these maps when analyzing SVs.
- Adding "padding" field to SV filter form (regulatory tab).
- Celerybeat tasks in ``variants`` app are now executing again.
- Fixed ``check_installation`` management command.
  Index for ``dbsnp`` was missing.
- Bumped chromedriver version to 87.
- Fixed bug where file export was not possible when nubmer of resulting variants were < 10.
- Fixed bug that made it impossible to properly sort by genotype in the results table.
- Cases can now be annotated with phenotypes and diseases.
  To speed up annotation, all phenotypes of all previous queries are listed for copy and paste.
  SODAR can also be queried for phenotypes.
- Properly sanitized output by Exomiser.
- Rebuild of variant summary database table happens every Sunday at 2:22am.
- Added celery queues ``maintenance`` and ``export``.
- Adding support for connecting two sites via the GAGH Beacon protocol.
- Adding link-out to "GenCC".
- Adding "submit to SPANR" feature.

Full Change List
================

- Fixed occasionally breaking tests ``ProjectExportTest`` by sorting member list.
  This bug didn't affect the correct output but wasn't consistent in the order of samples.
  Reason for this is unknown but might be that the order of cases a project is not always returned as in order they were created.
- Fixed above mentioned bug again by consolidating two distinct ``Meta`` classes in ``Case`` model.
- Fixed bug in SV tests that became visibly by above fix and created an additional variant that wasn't intended.
- Adapted core installation instructions in manual for latest data release and introduced use of VarFish API for import.
- Adding ``regmaps`` app for regulatory maps.
- Allowing users to specify padding for regulatory elements.
- Celerybeat tasks in ``variants`` app are now executing again.
  Issue was a wrong decorator.
- Fixed ``check_installation`` management command.
  Index for ``dbsnp`` was missing.
- Bumped chromedriver version to 87.
- Fixed bug where file export was not possible when number of resulting variants were < 10.
- Fixed bug that made it impossible to properly sort by genotype in the results table.
- Adding tests for upstream sychronization backend code.
- Allowing users with the Contributor role to a project to annotate cases with phenotype and disease terms.
  They can obtain the phenotypes from all queries of all users for a case and also fetch them from SODAR.
- Adding files for building Docker images and documenting Docker (Compose) deployment.
- Properly sanitized output by Exomiser.
- Rebuild of variant summary database table happens every Sunday at 2:22am.
- Added celery queues ``maintenance`` and ``export``.
- Adding support for connecting two sites via the GAGH Beacon protocol.
- Making CADD version behind CADD REST API configurable.
- Adding link-out to "GenCC".
- Adding "submit to SPANR" feature.

-------
v0.22.1
-------

End-User Summary
================

- Bumping chromedriver version.
- Fixed extra-annos import.

Full Change List
================

- Bumping chromedriver version.
- Fixed extra-annos import.

-------
v0.22.0
-------

End-User Summary
================

- Fixed bug where some variant flags didn't color the row in filtering results after reloading the page.
- Fixed upload bug in VarFish Kiosk when vcf file was too small.
- Blocking upload of VCF files with GRCh38/hg38/hg19 builds for VarFish Kiosk.
- Support for displaying GATK-gCNV SVs.
- Tracking global maintenance jobs with background jobs and displaying them to super user.
- Adding "Submit to CADD" feature similar to "Submit to MutationDistiller".
- Increased default frequency setting of HelixMTdb max hom filter to 200 for strict and 400 for relaxed.
- It is now possible to delete ACMG ratings by clearing the form and saving it.
- Fixed bug when inheritance preset was wrongly selected when switching to ``variant`` in an index-only case.
- Added hemizygous counts filter option to frequency filter form.
- Added ``synonymous`` effect to be also selected when checking ``all coding/deep intronic`` preset.
- Saving uploads pre-checking in kiosk mode to facilitate debugging.
- Kiosk mode also accepts VCFs based on hg19.
- VariantValidator output now displays three-letter representation of AA.
- Documented new clinvar aggregation method and VarFish "point rating".
- Implemented new clinvar data display in variant detail.
- Added feature to assemble cohorts from cases spanning multiple projects and filter for them in a project-like query.
- Added column to results list indicating if a variant lies in a disease gene, i.e. a gene listed in OMIM.
- Displaying warning if priorization is not enabled when entering HPO terms.
- Added possibility to import "extra annotations" for display along with the variants.
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
- "1" is now registered as heterozygous and homozygous state in genotype filter.
- Loading annotation and QC tabs in project cases list asyncronously.
- Increased timeout for VariantValidator response to 30 seconds.
- Digesting more VariantValidator responses.
- Fixed bug where when re-importing a case, the sample variants stats computation was performed on the member list of the old case.
  This could lead to the inconsistent state that when new members where added, the stats were not available for them.
  This lead to a 500 error when displaying the case overview page.
- Fixed missing QC plots in case detail view.
- Fixed bug in case VCF export where a variant existing twice in the results was breaking the export.
- Fixed log entries for file export when pathogenicity or phenotype scoring was activated.
- Bumped Chrome Driver version to 84 to be compatible with gitlab CI.
- CADD is now selected as default in pathogenicity scoring form (when available).
- Added global maintenance commands to clear old kiosk cases, inactive variant sets and expired exported files.
- Added ``SvAnnotationReleaseInfo`` model, information is filled during import and displayed in case detail view.
- Fixed bug that left number of small variants empty when they actually existed.
- Increased logging during case import.
- Marked old style import as deprecated.
- Fixed bug that prevented re-import of SVs.
- Fixed bug where a re-import of genotypes was not possible when the same variant types weren't present as in the initial import.
- Fixed bug where ``imported`` state of ``CaseImportInfo`` was already set after importing the first variant set.
- Integrated Genomics England PanelApp.
- Added command to check selected indexes and data types in database.
- Added columns to results table: ``cDNA effect``, ``protein effect``, ``effect text``, ``distance to splicesite``.
- Made effect columns and ``distance to splicesite`` column hide-able.
- Added warning to project/cohort query when a user tries to load previous results where not all variants are accessible.
- Renamed all occurrences of whitelist to allowlist and of blacklist to blocklist (sticking to what google introduced in their products).
- Fixed bug where cases were not deletable when using Chrome browser.
- Harmonized computation for relatedness in project-wide QC and in case QC (thus showing the same results if project only contains one family).
- Fixed failing case API re-import when user is not owner of previous import.
- Added ``PROJECTROLES_EMAIL_`` to config.
- Avoiding variants with asterisk alternative alleles.

Full Change List
================

- Fixed bug where some variant flags didn't color the row in filtering results after reloading the page.
- Fixed upload bug in VarFish Kiosk when vcf file was too small and the file copy process didn't flush the file completely resulting in only a parly available header.
- Blocking upload of VCF files with GRCh38/hg38/hg19 builds for VarFish Kiosk.
- Bumping sodar-core dependency to v0.8.1.
- Using new sodar-core REST API infrastructure.
- Using sodar-core tokens app instead of local one.
- Support for displaying GATK-gCNV SVs.
- Fix of REST API-based import.
- Tracking global maintenance jobs with background jobs.
- Global background jobs are displayed with site plugin point via bgjobs.
- Bumping Chromedriver to make CI work.
- Adding "Submit to CADD" feature similar to "Submit to MutationDistiller".
- Increased default frequency setting of HelixMTdb max hom filter to 200 for strict and 400 for relaxed.
- It is now possible to delete ACMG ratings by clearing the form and saving it.
- Updated reference and contact information.
- File upload in Kiosk mode now checks for VCF file without samples.
- Fixed bug when inheritance preset was wrongly selected when switching to ``variant`` in an index-only case.
- Added hemizygous counts filter option to frequency filter form.
- Added ``synonymous`` effect to be also selected when checking ``all coding/deep intronic`` preset.
- Saving uploads pre-checking in kiosk mode to facilitate debugging.
- Kiosk mode also accepts VCFs based on hg19.
- VariantValidator output now displays three-letter representation of AA.
- Documented new clinvar aggregation method and VarFish "point rating".
- Implemented new clinvar data display in variant detail.
- Case/project overview allows to download all annotated variants as a file now.
- Querying for annotated variants on the case/project overview now uses the common query infrastructure.
- Updating plotly to v0.54.5 (displays message on missing WebGL).
- Added feature to assemble cohorts from cases spanning multiple projects and filter for them in a project-like query.
- Added column to results list indicating if a variant lies in a disease gene, i.e. a gene listed in OMIM.
- Displaying warning if priorization is not enabled when entering HPO terms.
- Added possibility to import "extra annotations" for display along with the variants.
- On sites deployed by BIH CUBI, we make the CADD, SpliceAI, MMSp, and dbscSNV scores available.
- In priorization mode, ORPHA and DECIPHER terms are now selectable.
- Fixed bug of wrong order when sorting by LOEUF score.
- Adding some UI documenation.
- Fixed bug where case alignment stats were not properly imported.
  Refactored case import in a sense that the new variant set gets activated when it is successfully imported.
- Fixed bug where unfolding smallvariant details of a variant in a cohort that was not part of the base project caused a 404 error.
- Fixed bug that prevented case import from API.
- Increased speed of listing cases in case list view.
- Fixed bug that prevented export of project-wide filter results as XLS file.
- Adjusted genotype quality relaxed filter setting to 10.
- Added column with family name to results table of joint filtration.
- Added export of filter settings as JSON to structural variant filter form.
- Varseak Splicing link-out also considers refseq transcript.
  This could lead to inconsistency when Varseak picked the wrong transcript to the HGVS information.
- Fixed bug that occurred when sample statistics were available but sample was marked with having no genotype.
- Adjusted genotype quality strict filter setting to 10.
- Added possibility to export VCF file for cohorts.
- Increased logging during sample variant statistics computation.
- Using gnomAD exomes as initially selected frequency in results table.
- Using CADD as initially selected score metric in prioritization form.
- Fixed missing disease gene and mode of inheritance annotation in project/cohort filter results table.
- Catching errors during Kiosk annotation step properly.
- Fixed issues with file extension check in Kiosk mode during upload.
- "1" is now registered as heterozygous and homozygous state in genotype filter.
- Loading annotation and QC tabs in project cases list asyncronously.
- Increased timeout for VariantValidator response to 30 seconds.
- Digesting more VariantValidator responses, namely ``intergenic_variant_\d+`` and ``validation_warning_\d+``.
- Fixed bug where when re-importing a case, the sample variants stats computation was performed on the member list of the old case.
  This could lead to the inconsistent state that when new members where added, the stats were not available for them.
  This lead to a 500 error when displaying the case overview page.
- Fixed missing QC plots in case detail view.
- Fixed bug in case VCF export where a variant existing twice in the results was breaking the export.
- Fixed log entries for file export when pathogenicity or phenotype scoring was activated.
  The variants are sorted by score in this case which led to messy logging which was designed for logging when the chromosome changes.
- Bumped Chrome Driver version to 84 to be compatible with gitlab CI.
- CADD is now selected as default in pathogenicity scoring form (when available).
- Added global maintenance commands to clear old kiosk cases, inactive variant sets and expired exported files.
- Added ``SvAnnotationReleaseInfo`` model, information is filled during import and displayed in case detail view.
- Fixed bug that left number of small variants empty when they actually existed.
  This happened when SNVs and SVs were imported at the same time.
- Increased logging during case import.
- Marked old style import as deprecated.
- Fixed bug that prevented re-import of SVs by altering the unique constraint on the ``StructuralVariant`` table.
- Fixed bug where a re-import of genotypes was not possible when the same variant types weren't present as in the initial import.
  This was done by adding a ``state`` field to the ``VariantSetImportInfo`` model.
- Fixed bug where ``imported`` state of ``CaseImportInfo`` was already set after importing the first variant set.
- Integrated Genomics England PanelApp via their API.
- Added command to check selected indexes and data types in database.
- Added columns to results table: ``cDNA effect``, ``protein effect``, ``effect text``, ``distance to splicesite``.
- Made effect columns and ``distance to splicesite`` column hide-able.
- Added warning to project/cohort query when a user tries to load previous results where not all variants are accessible.
- Renamed all occurrences of whitelist to allowlist and of blacklist to blocklist (sticking to what google introduced in their products).
- Fixed bug where cases were not deletable when using Chrome browser.
- Harmonized computation for relatedness in project-wide QC and in case QC (thus showing the same results if project only contains one family).
- Fixed failing case API re-import when user is not owner of previous import.
  Now also all users with access to the project (except guests) can list the cases.
- Added ``PROJECTROLES_EMAIL_`` to config.
- Avoiding variants with asterisk alternative alleles.

-------
v0.21.0
-------

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
- Added more documentation throughout the UI.
- Added option to toggle displaying of logs during filtration, by default they are hidden.
- Fixed broken displaying of inhouse frequencies in variant detail view.
- Added variant annotation list (comments, flags, ACMG ratings) to project-wide info page.
- Row in filter results now turns gray when any flag is set (except bookmark flag; summary flag still colours in other colour).
- Fixed bug where comments and flags in variant details weren't updated when the variant details have been opened before.
- Added QC TSV download and per-sample metrics table to projec-wide QC.
- Removed ExAC locus link in result list, added gnomAD link to gene.
- Catching connection exceptions during file export with enabled pathogenicity and/or phenotype scoring.
- Fixed project/case search that delivered search results for projects that the searching user had no access to (only search was affected, access was not granted).
- Made case comments count change in real time.

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
- Added more documentation throughout the UI.
- Added option to toggle displaying of logs during filtration, by default they are hidden.
- Fixed broken displaying of inhouse frequencies in variant detail view.
- Added variant annotation list (comments, flags, ACMG ratings) to project-wide info page.
- Row in filter results now turns gray when any flag is set (except bookmark flag; summary flag still colours in other colour).
- Fixed bug where comments and flags in variant details weren't updated when the variant details have been opened before.
- Added QC TSV download and per-sample metrics table to projec-wide QC.
- Removed ExAC locus link in result list, added gnomAD link to gene.
- Catching connection exceptions during file export with enabled pathogenicity and/or phenotype scoring.
- Fixed project/case search that delivered search results for projects that the searching user had no access to (only search was affected, access was not granted).
- Made case comments count change in real time.

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
- Adding REST API for ``Case``.
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
- Extending the manual with SOPs and guidelines.

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
- Extending the manual with SOPs and guidelines.

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
