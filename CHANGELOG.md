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

## 0.1.0 (2024-07-02)


### Features

* adapt filter frontend to case detail variant annotations ([#1104](https://github.com/varfish-org/varfish-server/issues/1104)) ([#1122](https://github.com/varfish-org/varfish-server/issues/1122)) ([ed0652a](https://github.com/varfish-org/varfish-server/commit/ed0652a32840e050f121ecf46160efca7f796e60))
* add a flag for incidental findings ([#1121](https://github.com/varfish-org/varfish-server/issues/1121)) ([#1466](https://github.com/varfish-org/varfish-server/issues/1466)) ([04bd4f6](https://github.com/varfish-org/varfish-server/commit/04bd4f6f4b84f39b8daf6c72a42371178c96aef1))
* add api endpoints and front end for new qc data ([#1144](https://github.com/varfish-org/varfish-server/issues/1144)) ([#1146](https://github.com/varfish-org/varfish-server/issues/1146)) ([62416c5](https://github.com/varfish-org/varfish-server/commit/62416c5f0563391387531ac0ab538fa81acdbf9b))
* add cases_import settings for server to import from ([#1020](https://github.com/varfish-org/varfish-server/issues/1020)) ([#1025](https://github.com/varfish-org/varfish-server/issues/1025)) ([b7b5f4c](https://github.com/varfish-org/varfish-server/commit/b7b5f4cbc2ed96b1b369a957cc910b0c8ea4af39))
* add clear button for gene selection ([#1580](https://github.com/varfish-org/varfish-server/issues/1580)) ([#1626](https://github.com/varfish-org/varfish-server/issues/1626)) ([6a308f5](https://github.com/varfish-org/varfish-server/commit/6a308f5dfde372330f3880482b5e98a8948cd550))
* add manage.py initdev command ([#1767](https://github.com/varfish-org/varfish-server/issues/1767)) ([#1768](https://github.com/varfish-org/varfish-server/issues/1768)) ([f249d93](https://github.com/varfish-org/varfish-server/commit/f249d9390a1138046eb41129564557c347122b43))
* add seqmeta app to store available enrichment kits ([#19](https://github.com/varfish-org/varfish-server/issues/19)) ([#976](https://github.com/varfish-org/varfish-server/issues/976)) ([a0a6cfb](https://github.com/varfish-org/varfish-server/commit/a0a6cfb7affd43275fd46eb197f1592ecab05327))
* add settings export and import to vue sv interface ([#1453](https://github.com/varfish-org/varfish-server/issues/1453)) ([#1456](https://github.com/varfish-org/varfish-server/issues/1456)) ([6da6f43](https://github.com/varfish-org/varfish-server/commit/6da6f4371ca59533a955194b8ef92784ad7df8fb))
* add support for importing per-case seqvar VCF ([#1048](https://github.com/varfish-org/varfish-server/issues/1048)) ([#1155](https://github.com/varfish-org/varfish-server/issues/1155)) ([f2541e1](https://github.com/varfish-org/varfish-server/commit/f2541e105ae3b9128bb5147ccbe552c106466962))
* adding cases_analysis module ([#1735](https://github.com/varfish-org/varfish-server/issues/1735)) ([#1739](https://github.com/varfish-org/varfish-server/issues/1739)) ([7ac94eb](https://github.com/varfish-org/varfish-server/commit/7ac94eb9c4406fc0e4ef98a6fa39dcf2b9e933eb))
* adding cases_qc app with initial support for Dragen QC ([#1136](https://github.com/varfish-org/varfish-server/issues/1136)) ([9792b29](https://github.com/varfish-org/varfish-server/commit/9792b2925d2e56bf4accab5069e8effce25a073f))
* adding models and APIs for cases_import app ([#1021](https://github.com/varfish-org/varfish-server/issues/1021)) ([#1035](https://github.com/varfish-org/varfish-server/issues/1035)) ([5f847a5](https://github.com/varfish-org/varfish-server/commit/5f847a56894574767fb2059fb843ff4c9e769e43))
* adding persistent variant annotation ([#1185](https://github.com/varfish-org/varfish-server/issues/1185)) ([#1198](https://github.com/varfish-org/varfish-server/issues/1198)) ([0b428a0](https://github.com/varfish-org/varfish-server/commit/0b428a0b3ae713cccff33969982f16c0a16db85f))
* adding seqvars module ([#1737](https://github.com/varfish-org/varfish-server/issues/1737)) ([#1761](https://github.com/varfish-org/varfish-server/issues/1761)) ([4bab348](https://github.com/varfish-org/varfish-server/commit/4bab3481644875ae187c091e8438d3020b54f5ba))
* adding support for cramino and ngs-bits QC ([#1141](https://github.com/varfish-org/varfish-server/issues/1141)) ([#1143](https://github.com/varfish-org/varfish-server/issues/1143)) ([5cfec30](https://github.com/varfish-org/varfish-server/commit/5cfec30b824dedd1c26966993a148280e3fc31bf))
* adding support for importing samtools/bcftools stats ([#1139](https://github.com/varfish-org/varfish-server/issues/1139)) ([#1140](https://github.com/varfish-org/varfish-server/issues/1140)) ([7f03b6e](https://github.com/varfish-org/varfish-server/commit/7f03b6e782e03840bfb5b45b34fe908e7602a45f))
* adjust varfish-server to unified gnomAD SV dbs ([#1395](https://github.com/varfish-org/varfish-server/issues/1395)) ([#1397](https://github.com/varfish-org/varfish-server/issues/1397)) ([5f20f68](https://github.com/varfish-org/varfish-server/commit/5f20f6809746b750068ddad746022a37c0f3ecbe))
* allow direct opening of variant details via results table ([#1057](https://github.com/varfish-org/varfish-server/issues/1057))  ([#1081](https://github.com/varfish-org/varfish-server/issues/1081)) ([a7274fb](https://github.com/varfish-org/varfish-server/commit/a7274fb955d136262975bf3d377a919fc74a85f4))
* allow direct opening of variant details via results table ([#871](https://github.com/varfish-org/varfish-server/issues/871)) ([#1056](https://github.com/varfish-org/varfish-server/issues/1056)) ([1d91727](https://github.com/varfish-org/varfish-server/commit/1d91727ad8bca917c091c764d0d30e889f10fecf))
* allow sorting by extra annotations ([#1070](https://github.com/varfish-org/varfish-server/issues/1070)) ([#1074](https://github.com/varfish-org/varfish-server/issues/1074)) ([ee2d736](https://github.com/varfish-org/varfish-server/commit/ee2d736c619d683de6ae2cd6b52e0e87d3861e00))
* allow to see flags for same variant from other cases ([#733](https://github.com/varfish-org/varfish-server/issues/733)) ([#1531](https://github.com/varfish-org/varfish-server/issues/1531)) ([e5c12e4](https://github.com/varfish-org/varfish-server/commit/e5c12e45dca9d70d450f3c59920e27b69ecbc8c2))
* allow using secret files for secrets ([#1257](https://github.com/varfish-org/varfish-server/issues/1257)) ([#1258](https://github.com/varfish-org/varfish-server/issues/1258)) ([4ad84ac](https://github.com/varfish-org/varfish-server/commit/4ad84ac3d8d9908cf1bd54438cd3c5912a2e9ad5))
* AUTH parameters for TLS encrypted LDAP ([#1245](https://github.com/varfish-org/varfish-server/issues/1245)) ([#1246](https://github.com/varfish-org/varfish-server/issues/1246)) ([9b5d507](https://github.com/varfish-org/varfish-server/commit/9b5d507c581058ab8a5f5809173ca830f45af108))
* bootstrapping cases_import app ([#1019](https://github.com/varfish-org/varfish-server/issues/1019)) ([#1024](https://github.com/varfish-org/varfish-server/issues/1024)) ([e7d317e](https://github.com/varfish-org/varfish-server/commit/e7d317e7376c11b850339797a54720343b90a494))
* bring over small variant details changes to SVs ([#1089](https://github.com/varfish-org/varfish-server/issues/1089)) ([#1090](https://github.com/varfish-org/varfish-server/issues/1090)) ([56761c8](https://github.com/varfish-org/varfish-server/commit/56761c8c542a609985aa2c6a7d92177d79d8711a))
* bump storybook version to 7 ([#1091](https://github.com/varfish-org/varfish-server/issues/1091)) ([#1095](https://github.com/varfish-org/varfish-server/issues/1095)) ([bfec8a8](https://github.com/varfish-org/varfish-server/commit/bfec8a8cecefb3aab3970e904c800a9ae4c0aa72))
* change label of final causativereported to final report ([#665](https://github.com/varfish-org/varfish-server/issues/665)) ([#1349](https://github.com/varfish-org/varfish-server/issues/1349)) ([b0bc5fc](https://github.com/varfish-org/varfish-server/commit/b0bc5fcd602de16c38bd1f4b1607c0f67b48af88))
* change types of id column and sequence for large tables ([#462](https://github.com/varfish-org/varfish-server/issues/462)) ([#1350](https://github.com/varfish-org/varfish-server/issues/1350)) ([9d63c7c](https://github.com/varfish-org/varfish-server/commit/9d63c7cef9dfc699c8bb32e3ab6c87c34ed84e2e))
* delete clinvar_export app ([#1664](https://github.com/varfish-org/varfish-server/issues/1664)) ([#1762](https://github.com/varfish-org/varfish-server/issues/1762)) ([e75275c](https://github.com/varfish-org/varfish-server/commit/e75275c48bd1ac1ae127ef8d5481800c75d38617))
* display ClinVar and GTEx values for each gene ([#672](https://github.com/varfish-org/varfish-server/issues/672), [#68](https://github.com/varfish-org/varfish-server/issues/68)) ([#1129](https://github.com/varfish-org/varfish-server/issues/1129)) ([6c83a00](https://github.com/varfish-org/varfish-server/commit/6c83a00c24ed606cc6a93d80811e37fc3727f58b))
* enable SpliceAI and CADD-PHRED columns if available ([#1069](https://github.com/varfish-org/varfish-server/issues/1069)) ([#1073](https://github.com/varfish-org/varfish-server/issues/1073)) ([885bc13](https://github.com/varfish-org/varfish-server/commit/885bc136caef3c8c1f18e4022c9490b39371fbed))
* flatten the "More..." tabs ([#1059](https://github.com/varfish-org/varfish-server/issues/1059)) ([#1060](https://github.com/varfish-org/varfish-server/issues/1060)) ([7a828c5](https://github.com/varfish-org/varfish-server/commit/7a828c582a2c1e7dc4aed67f7e2d3b79e5a71d3b))
* hgmd pro link out missing in the vue interface ([#1632](https://github.com/varfish-org/varfish-server/issues/1632)) ([#1677](https://github.com/varfish-org/varfish-server/issues/1677)) ([f98c060](https://github.com/varfish-org/varfish-server/commit/f98c0609c72bfde8d9608d20990bbdd4fc27babb))
* improving gene list display for many genes ([#1092](https://github.com/varfish-org/varfish-server/issues/1092)) ([#1093](https://github.com/varfish-org/varfish-server/issues/1093)) ([d8785cb](https://github.com/varfish-org/varfish-server/commit/d8785cbd72c534f8c323e3f538e4d7c4cd172b65))
* indicate clicked variant when returning from variant details ([#1526](https://github.com/varfish-org/varfish-server/issues/1526)) ([#1561](https://github.com/varfish-org/varfish-server/issues/1561)) ([c4bc4ef](https://github.com/varfish-org/varfish-server/commit/c4bc4efa9dea01d3763af592655f5fa5a15d1bcb))
* integrate ClinGen, sHet, rCNV gene information ([#1119](https://github.com/varfish-org/varfish-server/issues/1119)) ([1fbaf40](https://github.com/varfish-org/varfish-server/commit/1fbaf407171a95838d24dcd6d56ac6369a864bd3))
* integrate seqvar details page from REEV ([#1300](https://github.com/varfish-org/varfish-server/issues/1300)) ([#1369](https://github.com/varfish-org/varfish-server/issues/1369)) ([a8f6da1](https://github.com/varfish-org/varfish-server/commit/a8f6da17a3862724a401d14a59c4d7eec70d43a9))
* integrate SV filtration by sv_type/tx impact ([#986](https://github.com/varfish-org/varfish-server/issues/986)) ([#995](https://github.com/varfish-org/varfish-server/issues/995)) ([e9393b5](https://github.com/varfish-org/varfish-server/commit/e9393b528f37221f00d24faee66270767d9f31d4))
* integration of drf-spectacular for OpenAPI schema generation ([#1405](https://github.com/varfish-org/varfish-server/issues/1405)) ([53a972a](https://github.com/varfish-org/varfish-server/commit/53a972a1f3a0a8eac640277303c5ea4197cc9767))
* integration of strucvars from REEV ([#1300](https://github.com/varfish-org/varfish-server/issues/1300)) ([#1379](https://github.com/varfish-org/varfish-server/issues/1379)) ([c596e0c](https://github.com/varfish-org/varfish-server/commit/c596e0c53c9625abe30f02e18cf4334f1e7d12c9))
* integration of worker "seqvars ingest" ([#1189](https://github.com/varfish-org/varfish-server/issues/1189)) ([ead404a](https://github.com/varfish-org/varfish-server/commit/ead404a5f203e57f5c9410b1bf1b48ed200830b3))
* integration of worker "strucvars ingest" ([#1190](https://github.com/varfish-org/varfish-server/issues/1190)) ([79cc5e7](https://github.com/varfish-org/varfish-server/commit/79cc5e71b02791c14b8079c810f470de753b6088))
* keep table after viewing variant details and going back to the variant table ([#1273](https://github.com/varfish-org/varfish-server/issues/1273)) ([#1464](https://github.com/varfish-org/varfish-server/issues/1464)) ([d1f793c](https://github.com/varfish-org/varfish-server/commit/d1f793cdc212c436a70b251c36c0d4ad9ab6dab0))
* logging number of query result rows ([#1066](https://github.com/varfish-org/varfish-server/issues/1066)) ([#1076](https://github.com/varfish-org/varfish-server/issues/1076)) ([d9c4e84](https://github.com/varfish-org/varfish-server/commit/d9c4e848dd511f7f18c7dc71dd654e2e726b548e))
* prepare backend for case detail variant annotations ([#1099](https://github.com/varfish-org/varfish-server/issues/1099)) ([#1105](https://github.com/varfish-org/varfish-server/issues/1105)) ([28d18d2](https://github.com/varfish-org/varfish-server/commit/28d18d2e94d3cc39f54e3e385fc140fffc0333b8))
* prepare small variant models for storing results ([#966](https://github.com/varfish-org/varfish-server/issues/966)) ([#985](https://github.com/varfish-org/varfish-server/issues/985)) ([939a046](https://github.com/varfish-org/varfish-server/commit/939a0468eae9d4034408cf4559a67e7c24ac876e))
* provide acmg classification support for svs cnvs ([#469](https://github.com/varfish-org/varfish-server/issues/469)) ([#1643](https://github.com/varfish-org/varfish-server/issues/1643)) ([e6a9b44](https://github.com/varfish-org/varfish-server/commit/e6a9b444477338855f8e66c8931dbeacd1c568f1))
* provide genome browser through reverse proxy ([#1011](https://github.com/varfish-org/varfish-server/issues/1011)) ([#1015](https://github.com/varfish-org/varfish-server/issues/1015)) ([1e21de3](https://github.com/varfish-org/varfish-server/commit/1e21de32645e72ed0917b7f1dda4e3b490b8756d))
* qc values thresholds should be adjustable ([#1530](https://github.com/varfish-org/varfish-server/issues/1530)) ([#1644](https://github.com/varfish-org/varfish-server/issues/1644)) ([beed42c](https://github.com/varfish-org/varfish-server/commit/beed42c1880af30564d12edc29362fb7fcf93db1))
* removal of dependencies to geneinfo app ([#1635](https://github.com/varfish-org/varfish-server/issues/1635)) ([#1719](https://github.com/varfish-org/varfish-server/issues/1719)) ([48c1728](https://github.com/varfish-org/varfish-server/commit/48c17282b3fdce55cddccf0939655ebfe75104ab))
* remove necessity nltk data download ([#1259](https://github.com/varfish-org/varfish-server/issues/1259)) ([#1269](https://github.com/varfish-org/varfish-server/issues/1269)) ([c10a37f](https://github.com/varfish-org/varfish-server/commit/c10a37fb1a089d9670eb9c4374b721e57ea6cb6e))
* remove old filter features ([#739](https://github.com/varfish-org/varfish-server/issues/739)) ([#1628](https://github.com/varfish-org/varfish-server/issues/1628)) ([1ec5b3e](https://github.com/varfish-org/varfish-server/commit/1ec5b3e990372873282ba6ecd1bed576ab3ab243))
* remove references to old hgnc gene table in varfish ([#1551](https://github.com/varfish-org/varfish-server/issues/1551)) ([#1633](https://github.com/varfish-org/varfish-server/issues/1633)) ([dbe4fd4](https://github.com/varfish-org/varfish-server/commit/dbe4fd4352eae8a96d69243c822ba2ceae9cb9ce))
* searching for cases only works with exact match ([#1252](https://github.com/varfish-org/varfish-server/issues/1252)) ([#1270](https://github.com/varfish-org/varfish-server/issues/1270)) ([00edd75](https://github.com/varfish-org/varfish-server/commit/00edd75387564a79a8b58134265addad070ebec7))
* separator for gene list or hpo terms ([#1196](https://github.com/varfish-org/varfish-server/issues/1196)) ([#1480](https://github.com/varfish-org/varfish-server/issues/1480)) ([ba73b99](https://github.com/varfish-org/varfish-server/commit/ba73b9959c2bd8acbf576c3a4e18ee926058d620))
* set default query preset for project ([#1478](https://github.com/varfish-org/varfish-server/issues/1478)) ([#1611](https://github.com/varfish-org/varfish-server/issues/1611)) ([a1ab0ff](https://github.com/varfish-org/varfish-server/commit/a1ab0ff55567f1292238e92301102677cc2bbaf1))
* set default query preset for project ([#1478](https://github.com/varfish-org/varfish-server/issues/1478)) ([#1622](https://github.com/varfish-org/varfish-server/issues/1622)) ([b28ca91](https://github.com/varfish-org/varfish-server/commit/b28ca91f18c55e3fb6bd306fa664fe5f975ed5fd))
* show flags comments from other cases in variant result table ([#1564](https://github.com/varfish-org/varfish-server/issues/1564)) ([#1660](https://github.com/varfish-org/varfish-server/issues/1660)) ([687f0ca](https://github.com/varfish-org/varfish-server/commit/687f0ca45f7c6139d592b8d63784fb282fb1f30d))
* small variant artifact button should have hover description ([#1118](https://github.com/varfish-org/varfish-server/issues/1118)) ([#1477](https://github.com/varfish-org/varfish-server/issues/1477)) ([64e979a](https://github.com/varfish-org/varfish-server/commit/64e979a00ec5ed8cb3cceeacfed7ae69cad9b7ad))
* switching to builtin OpenAPI generation from drf ([#1734](https://github.com/varfish-org/varfish-server/issues/1734)) ([9561fb4](https://github.com/varfish-org/varfish-server/commit/9561fb4d52f1bde2225fb4c333cf7195e230b5c6))
* update SV filtration filters ([#1094](https://github.com/varfish-org/varfish-server/issues/1094))) ([#1098](https://github.com/varfish-org/varfish-server/issues/1098)) ([e0e3da2](https://github.com/varfish-org/varfish-server/commit/e0e3da2f8b7061daafa2b41c3329a313712f8149))
* upgrade to sodar core 0.13.0 ([#1113](https://github.com/varfish-org/varfish-server/issues/1113)) ([#1114](https://github.com/varfish-org/varfish-server/issues/1114)) ([0111247](https://github.com/varfish-org/varfish-server/commit/0111247fd20be347052ae00d963994d9509f7f9d))
* use annonars REST API services for small variant details ([#1084](https://github.com/varfish-org/varfish-server/issues/1084)) ([#1087](https://github.com/varfish-org/varfish-server/issues/1087)) ([b7e8015](https://github.com/varfish-org/varfish-server/commit/b7e8015e1a9d71628c300b2ea37377452c365b60))
* use CADD as default prioritization score ([#1063](https://github.com/varfish-org/varfish-server/issues/1063)) ([#1075](https://github.com/varfish-org/varfish-server/issues/1075)) ([23fc1a3](https://github.com/varfish-org/varfish-server/commit/23fc1a37a869fcb80434245b67807059365ff303))
* viewing comments of variants in other samples ([#964](https://github.com/varfish-org/varfish-server/issues/964)) ([#1508](https://github.com/varfish-org/varfish-server/issues/1508)) ([bbd1348](https://github.com/varfish-org/varfish-server/commit/bbd134865f9ceea602ac18cd634264ee2ba58e54))


### Bug Fixes

* __vite_mapDeps not defined issue ([#1373](https://github.com/varfish-org/varfish-server/issues/1373)) ([4b226f8](https://github.com/varfish-org/varfish-server/commit/4b226f8ba102a5b43b7eba98b2c946c4faec579e))
* adapting strucvar details to latest annonars changes ([#1229](https://github.com/varfish-org/varfish-server/issues/1229)) ([#1232](https://github.com/varfish-org/varfish-server/issues/1232)) ([b472a7c](https://github.com/varfish-org/varfish-server/commit/b472a7c5d134a586b05051294e009e66ab168d3a))
* add missing dependencies to Dockerfile ([#996](https://github.com/varfish-org/varfish-server/issues/996)) ([0fe8219](https://github.com/varfish-org/varfish-server/commit/0fe8219c606c75e155a4fbc131805426c654dcc1))
* add missing labels in variant frequency details ([#1064](https://github.com/varfish-org/varfish-server/issues/1064)) ([#1077](https://github.com/varfish-org/varfish-server/issues/1077)) ([1206181](https://github.com/varfish-org/varfish-server/commit/12061817db1aff5034572d8185655ad24fd95e8e))
* add necessary tag for login page ([#1012](https://github.com/varfish-org/varfish-server/issues/1012)) ([9a40f67](https://github.com/varfish-org/varfish-server/commit/9a40f673fb6f015ba30da065ef1533bb0945268e))
* Add param to igv jump ([#1406](https://github.com/varfish-org/varfish-server/issues/1406)) ([2903065](https://github.com/varfish-org/varfish-server/commit/2903065d41a155125bf514681123ab62263e52eb))
* adding back default columns ([#1127](https://github.com/varfish-org/varfish-server/issues/1127)) ([4fdc459](https://github.com/varfish-org/varfish-server/commit/4fdc459046aff7d52f0d69d0afc7c95f3d581d2a))
* adding large panels causes incorrect linting errors ([#1184](https://github.com/varfish-org/varfish-server/issues/1184)) ([#1250](https://github.com/varfish-org/varfish-server/issues/1250)) ([feb0885](https://github.com/varfish-org/varfish-server/commit/feb08852e024ed65373aaa77c1f83ab60c29f0b2))
* adjust mt chromosome in igv calls ([#1562](https://github.com/varfish-org/varfish-server/issues/1562)) ([#1563](https://github.com/varfish-org/varfish-server/issues/1563)) ([a28a279](https://github.com/varfish-org/varfish-server/commit/a28a279603d7d621b1454cfcda80f454f982d512))
* adjusting frontend code to changes in backend ([#1224](https://github.com/varfish-org/varfish-server/issues/1224), [#1225](https://github.com/varfish-org/varfish-server/issues/1225)) ([#1228](https://github.com/varfish-org/varfish-server/issues/1228)) ([0537ed0](https://github.com/varfish-org/varfish-server/commit/0537ed027066f292da801dc63153f663109399a8))
* adjusting strucvar filter settings ([#984](https://github.com/varfish-org/varfish-server/issues/984)) ([94533b8](https://github.com/varfish-org/varfish-server/commit/94533b8e9176b155fc1d50e7a017ad550172776c))
* allow changing the number of rows and switching pages in structural variants table ([#1268](https://github.com/varfish-org/varfish-server/issues/1268)) ([#1309](https://github.com/varfish-org/varfish-server/issues/1309)) ([5c964af](https://github.com/varfish-org/varfish-server/commit/5c964af0a4291a56d671aee20925b266175b9c79))
* bump rfl to get bihealth/reev-frontend-lib[#163](https://github.com/varfish-org/varfish-server/issues/163) ([#1422](https://github.com/varfish-org/varfish-server/issues/1422)) ([85f1725](https://github.com/varfish-org/varfish-server/commit/85f1725ad522a4be288bfac7dec1c7c1e2caa6c8))
* bump rfl to get bihealth/reev-frontend-lib[#164](https://github.com/varfish-org/varfish-server/issues/164) ([#1423](https://github.com/varfish-org/varfish-server/issues/1423)) ([c53a830](https://github.com/varfish-org/varfish-server/commit/c53a830101ec6d766335cf2a715ccda357c6d348))
* caller splitting for old cases ([#1741](https://github.com/varfish-org/varfish-server/issues/1741)) ([#1742](https://github.com/varfish-org/varfish-server/issues/1742)) ([a9d9416](https://github.com/varfish-org/varfish-server/commit/a9d9416fe7e230eeaa0f7fb2ff627504f8867fe0))
* case details annotations tables unexpectedly empty in some cases ([#1312](https://github.com/varfish-org/varfish-server/issues/1312)) ([#1313](https://github.com/varfish-org/varfish-server/issues/1313)) ([4d4fa10](https://github.com/varfish-org/varfish-server/commit/4d4fa105c14e14c21b180bd97dbf53b24be91c5b))
* case not set on result set creation ([#1131](https://github.com/varfish-org/varfish-server/issues/1131)) ([2236a06](https://github.com/varfish-org/varfish-server/commit/2236a063881c5b6d6a448b25545b9fd9c46264c0))
* changed query presets only shown in filtering after page refresh ([#1557](https://github.com/varfish-org/varfish-server/issues/1557)) ([#1624](https://github.com/varfish-org/varfish-server/issues/1624)) ([dc66b1a](https://github.com/varfish-org/varfish-server/commit/dc66b1a61652961f4d2f46f602cfe72a05182ec6))
* cloning a user defined quick preset does not work ([#1482](https://github.com/varfish-org/varfish-server/issues/1482)) ([#1625](https://github.com/varfish-org/varfish-server/issues/1625)) ([f0e2ea8](https://github.com/varfish-org/varfish-server/commit/f0e2ea8d02a3359c80f222b32db310866e786403))
* coerce FORMAT/cn to int when writing SV VCF ([#1743](https://github.com/varfish-org/varfish-server/issues/1743)) ([#1744](https://github.com/varfish-org/varfish-server/issues/1744)) ([22ed8bd](https://github.com/varfish-org/varfish-server/commit/22ed8bd97bccdf9d0a2a1b821e004fae54dd6e4d))
* color of sv flags does not depend on summary status ([#1260](https://github.com/varfish-org/varfish-server/issues/1260)) ([#1325](https://github.com/varfish-org/varfish-server/issues/1325)) ([e5fb652](https://github.com/varfish-org/varfish-server/commit/e5fb65208894fe849e916614c1f8f4315c45fba3))
* compatible with mehari 0.8 ([#1174](https://github.com/varfish-org/varfish-server/issues/1174)) ([fe5a3dd](https://github.com/varfish-org/varfish-server/commit/fe5a3dde74c5e32ca15959e964b5ec2bd1b3b99f))
* compound het and recessive mode broken ([#1058](https://github.com/varfish-org/varfish-server/issues/1058)) ([#1078](https://github.com/varfish-org/varfish-server/issues/1078)) ([4b4da69](https://github.com/varfish-org/varfish-server/commit/4b4da69a13b5b6d49b30695a17b6cea361974040))
* current state of special result set ([#1377](https://github.com/varfish-org/varfish-server/issues/1377)) ([#1392](https://github.com/varfish-org/varfish-server/issues/1392)) ([5dbddde](https://github.com/varfish-org/varfish-server/commit/5dbddde7c8615b89b9390e63a0fc81b93454a12f))
* dbsnp int to bigint ([#1370](https://github.com/varfish-org/varfish-server/issues/1370)) ([baa17b0](https://github.com/varfish-org/varfish-server/commit/baa17b07e05caa59854aa41ac98a20d7ff9f5312))
* deleting a case broken ([#1162](https://github.com/varfish-org/varfish-server/issues/1162)) ([#1301](https://github.com/varfish-org/varfish-server/issues/1301)) ([0c2cf19](https://github.com/varfish-org/varfish-server/commit/0c2cf1996197dd678587841ff63266b020b57f17))
* display of clinical significance in per-gene table ([18c4a55](https://github.com/varfish-org/varfish-server/commit/18c4a552049cb78f7481727ea9b5641b07a98b48))
* display of variant flagscommentsacmg counts are static always 0 ([#1376](https://github.com/varfish-org/varfish-server/issues/1376)) ([#1437](https://github.com/varfish-org/varfish-server/issues/1437)) ([dbfd897](https://github.com/varfish-org/varfish-server/commit/dbfd8976e89e815427084acdfc9816e6792226e7))
* display SV gnomAD genomes counts, not exomes ([#1424](https://github.com/varfish-org/varfish-server/issues/1424)) ([f87b46e](https://github.com/varfish-org/varfish-server/commit/f87b46eeab5cf63ce2587159601abf4c2cf5b80d))
* distance to next exon setting is not properly interpreted ([#1029](https://github.com/varfish-org/varfish-server/issues/1029)) ([#1041](https://github.com/varfish-org/varfish-server/issues/1041)) ([1e5aaff](https://github.com/varfish-org/varfish-server/commit/1e5aaff54a4b106bb464819c920aec67dbb81407))
* distance to next exon should be reset when selecting a new quick preset ([#1256](https://github.com/varfish-org/varfish-server/issues/1256)) ([#1324](https://github.com/varfish-org/varfish-server/issues/1324)) ([432d6ce](https://github.com/varfish-org/varfish-server/commit/432d6ce460c8c659591fc0d4349d475dc2e817d9))
* effects all does not catch empty annotations ([#1578](https://github.com/varfish-org/varfish-server/issues/1578)) ([#1579](https://github.com/varfish-org/varfish-server/issues/1579)) ([6b8fc34](https://github.com/varfish-org/varfish-server/commit/6b8fc34de737801a37c2d49bba7dc8c98a56f0f1))
* enable strucvar view cards again ([#1403](https://github.com/varfish-org/varfish-server/issues/1403)) ([cadd418](https://github.com/varfish-org/varfish-server/commit/cadd418da6a6e9db4d9f641920210b3bfbd7823c))
* error in parsing chromosomal coordinates in genomic regions ([#989](https://github.com/varfish-org/varfish-server/issues/989)) ([#990](https://github.com/varfish-org/varfish-server/issues/990)) ([37533d0](https://github.com/varfish-org/varfish-server/commit/37533d05b091eeb311d9f38c4652a525ac708b4e))
* exomiser parameters are wrong ([#947](https://github.com/varfish-org/varfish-server/issues/947)) ([#1346](https://github.com/varfish-org/varfish-server/issues/1346)) ([0c3fb1c](https://github.com/varfish-org/varfish-server/commit/0c3fb1c94bdfcf8cbe04b21948c666f290b9950b))
* exomiser prioritization broken for some genes ([#1085](https://github.com/varfish-org/varfish-server/issues/1085)) ([#1086](https://github.com/varfish-org/varfish-server/issues/1086)) ([52063d1](https://github.com/varfish-org/varfish-server/commit/52063d16ce9ab361989d459f065cade1c9ffc5ab))
* fielderror cannot resolve keyword genotype into field ([#988](https://github.com/varfish-org/varfish-server/issues/988)) ([#991](https://github.com/varfish-org/varfish-server/issues/991)) ([1e5a12b](https://github.com/varfish-org/varfish-server/commit/1e5a12b61b1308042bf40869965a09ad51dcb80f))
* file export mehari call is external ([#1535](https://github.com/varfish-org/varfish-server/issues/1535)) ([#1536](https://github.com/varfish-org/varfish-server/issues/1536)) ([e662764](https://github.com/varfish-org/varfish-server/commit/e6627640311cbbe2486de0576339615923d84d81))
* fix SV flagging issue with BND/INS types ([#1088](https://github.com/varfish-org/varfish-server/issues/1088)) ([6a27732](https://github.com/varfish-org/varfish-server/commit/6a27732d464b41ea53f37f2d1697ec51dba17c29))
* frontend build fails on machines less than 32gb ram ([#1720](https://github.com/varfish-org/varfish-server/issues/1720)) ([#1721](https://github.com/varfish-org/varfish-server/issues/1721)) ([c4ab0d8](https://github.com/varfish-org/varfish-server/commit/c4ab0d8dc082d1d82a6642bb6679eae27fd69757))
* further speed improvement loading small variant table ([#1037](https://github.com/varfish-org/varfish-server/issues/1037)) ([#1038](https://github.com/varfish-org/varfish-server/issues/1038)) ([5fe0c36](https://github.com/varfish-org/varfish-server/commit/5fe0c36a90449d57019a379525be1698152cb9f1))
* gene allowlist validation inconsistent in front- and back-end ([#1532](https://github.com/varfish-org/varfish-server/issues/1532)) ([#1538](https://github.com/varfish-org/varfish-server/issues/1538)) ([8917534](https://github.com/varfish-org/varfish-server/commit/891753402192085e277d9297369f71cf28d9e588))
* genomic regions are not stored correctly ([#992](https://github.com/varfish-org/varfish-server/issues/992)) ([#994](https://github.com/varfish-org/varfish-server/issues/994)) ([b6a4955](https://github.com/varfish-org/varfish-server/commit/b6a4955793415d78d5ccc7a4f2790b8d05bb357b))
* genomic regions are not stored correctly ([#992](https://github.com/varfish-org/varfish-server/issues/992)) ([#999](https://github.com/varfish-org/varfish-server/issues/999)) ([58a46ea](https://github.com/varfish-org/varfish-server/commit/58a46ea82544e63cabe7131bb8a15dfea92ee86c))
* high quality as default for sv filtration ([#984](https://github.com/varfish-org/varfish-server/issues/984)) ([#1027](https://github.com/varfish-org/varfish-server/issues/1027)) ([620eb8a](https://github.com/varfish-org/varfish-server/commit/620eb8a66a0ddf7793e81d69755dc4ebdeae9548))
* igv linkout does not work for mitochondrial positions ([#1283](https://github.com/varfish-org/varfish-server/issues/1283)) ([#1559](https://github.com/varfish-org/varfish-server/issues/1559)) ([1806783](https://github.com/varfish-org/varfish-server/commit/180678382e428d0cc7d5eca78c0eb64351209676))
* igv shows error for grch38 svs ([#1274](https://github.com/varfish-org/varfish-server/issues/1274)) ([#1323](https://github.com/varfish-org/varfish-server/issues/1323)) ([ac56b4e](https://github.com/varfish-org/varfish-server/commit/ac56b4e0ac90ce33ac0e8aa3fa3b1e2737a0b06b))
* igvjs view on variant details page does not jump to sv position ([#1560](https://github.com/varfish-org/varfish-server/issues/1560)) ([#1659](https://github.com/varfish-org/varfish-server/issues/1659)) ([9332f9a](https://github.com/varfish-org/varfish-server/commit/9332f9a09252f89c5ad851111bf67eb59d1e76dd))
* integration of worker latest version ([#1680](https://github.com/varfish-org/varfish-server/issues/1680)) ([ab441ff](https://github.com/varfish-org/varfish-server/commit/ab441ff89e8f129952994ff466b41611621ff912))
* issue with generating strucvar query JSON and empty values ([#974](https://github.com/varfish-org/varfish-server/issues/974)) ([f20877c](https://github.com/varfish-org/varfish-server/commit/f20877c9c685285ec5778253773dcaa5fafc6aa6))
* lift over orphaned variant annotations ([#1124](https://github.com/varfish-org/varfish-server/issues/1124)) ([#1126](https://github.com/varfish-org/varfish-server/issues/1126)) ([764440a](https://github.com/varfish-org/varfish-server/commit/764440a7b6b55d34b4b404c2042f52d29e8dc5de))
* limit seqvar details to gene from result row ([#1380](https://github.com/varfish-org/varfish-server/issues/1380)) ([#1404](https://github.com/varfish-org/varfish-server/issues/1404)) ([a194921](https://github.com/varfish-org/varfish-server/commit/a194921446d94eca7e60400f2afaa34c7180b006))
* make flagging SVs possible again ([#1006](https://github.com/varfish-org/varfish-server/issues/1006)) ([#1007](https://github.com/varfish-org/varfish-server/issues/1007)) ([cf9c1bb](https://github.com/varfish-org/varfish-server/commit/cf9c1bb779d9674e8f88545c2389b3fe10458f3b))
* make flags and comments for for SVs ([#1401](https://github.com/varfish-org/varfish-server/issues/1401)) ([252ca55](https://github.com/varfish-org/varfish-server/commit/252ca55433d8e3d5d185fad727f01783572a4ea2))
* make SV import work when feature-effects are empty ([#1040](https://github.com/varfish-org/varfish-server/issues/1040)) ([3da4367](https://github.com/varfish-org/varfish-server/commit/3da4367f1b98e44148f4c5ead8ea43835dabf385))
* making gnomAD frequency display work again ([#1108](https://github.com/varfish-org/varfish-server/issues/1108)) ([f92fb41](https://github.com/varfish-org/varfish-server/commit/f92fb4145eea59a13e841fa11d0c221d746a4ba0))
* mehari call ([#1199](https://github.com/varfish-org/varfish-server/issues/1199)) ([a43ebf4](https://github.com/varfish-org/varfish-server/commit/a43ebf4a67bf65815d0f63f5bb14b239dbd900ea))
* mehari call ([#1202](https://github.com/varfish-org/varfish-server/issues/1202)) ([2a9e3ba](https://github.com/varfish-org/varfish-server/commit/2a9e3ba6723800554f372db12ce8da1819880960))
* misleading no available data message on empty result sets ([#1275](https://github.com/varfish-org/varfish-server/issues/1275)) ([#1310](https://github.com/varfish-org/varfish-server/issues/1310)) ([2b16503](https://github.com/varfish-org/varfish-server/commit/2b1650316bf7f9a818ab3c5e736839dc33b11546))
* optional columns selected with each variant detail view ([#1111](https://github.com/varfish-org/varfish-server/issues/1111)) ([#1112](https://github.com/varfish-org/varfish-server/issues/1112)) ([3a49d08](https://github.com/varfish-org/varfish-server/commit/3a49d087127086c3810703430a6094f907a982ed))
* order link-outs alphabetically ([#1097](https://github.com/varfish-org/varfish-server/issues/1097)) ([e3a7043](https://github.com/varfish-org/varfish-server/commit/e3a704303a51f56c30b662c6c94986ceb2144fc1))
* permissions broken for smallvariant query ([#1013](https://github.com/varfish-org/varfish-server/issues/1013)) ([#1014](https://github.com/varfish-org/varfish-server/issues/1014)) ([5bf6b4d](https://github.com/varfish-org/varfish-server/commit/5bf6b4d0db196a1043b431836ca6d8b2f131c960))
* previous query is not restricted to user ([#1030](https://github.com/varfish-org/varfish-server/issues/1030)) ([#1080](https://github.com/varfish-org/varfish-server/issues/1080)) ([58ff28f](https://github.com/varfish-org/varfish-server/commit/58ff28f4675a8632697ca16f4b5a91f839116707))
* previous query settings might interfer with current settings ([#1629](https://github.com/varfish-org/varfish-server/issues/1629)) ([#1661](https://github.com/varfish-org/varfish-server/issues/1661)) ([7bcc365](https://github.com/varfish-org/varfish-server/commit/7bcc3650ac091410a8d6fac9fee280abf2c8631a))
* prioritizer and phenotype scoring not used in query ([#1016](https://github.com/varfish-org/varfish-server/issues/1016)) ([#1017](https://github.com/varfish-org/varfish-server/issues/1017)) ([69fd67a](https://github.com/varfish-org/varfish-server/commit/69fd67ac021f118e27d3b22e56d1daeb93f79b9e))
* properly handle all-null/"." REVEL etc. scores ([#1117](https://github.com/varfish-org/varfish-server/issues/1117)) ([#1130](https://github.com/varfish-org/varfish-server/issues/1130)) ([10afced](https://github.com/varfish-org/varfish-server/commit/10afced282396a025be6205530502c3775a855dd))
* properly link out in SV results table ([#1068](https://github.com/varfish-org/varfish-server/issues/1068)) ([#1072](https://github.com/varfish-org/varfish-server/issues/1072)) ([5ecd0cc](https://github.com/varfish-org/varfish-server/commit/5ecd0cc0946ec18493534031ef90ca5e40e482a7))
* properly load user annotations into stores ([#1197](https://github.com/varfish-org/varfish-server/issues/1197)) ([6bc4172](https://github.com/varfish-org/varfish-server/commit/6bc417213c3c2e1773d0ce20571ebaf285384325))
* properly reset factoryboy sequences when used with snapshot tests ([#1186](https://github.com/varfish-org/varfish-server/issues/1186)) ([0f641a2](https://github.com/varfish-org/varfish-server/commit/0f641a2dcf98e0924ecc6652c8a9d58b18fc9792))
* query preset cannot add gene regions presets ([#1166](https://github.com/varfish-org/varfish-server/issues/1166)) ([#1457](https://github.com/varfish-org/varfish-server/issues/1457)) ([6bc5bfb](https://github.com/varfish-org/varfish-server/commit/6bc5bfbca67f573475c3581a6ae57d23e23a3e14))
* query preset removing a quick preset does not remove preset ([#1165](https://github.com/varfish-org/varfish-server/issues/1165)) ([#1458](https://github.com/varfish-org/varfish-server/issues/1458)) ([e90e3a1](https://github.com/varfish-org/varfish-server/commit/e90e3a10f58a2f8136965e157af647369795acfd))
* query presets cannot add new quick preset ([#1164](https://github.com/varfish-org/varfish-server/issues/1164)) ([#1459](https://github.com/varfish-org/varfish-server/issues/1459)) ([39603c9](https://github.com/varfish-org/varfish-server/commit/39603c9c887e1c43d4eb78b9fdac24965d9d760b))
* query presets cannot add new quick preset ([#1164](https://github.com/varfish-org/varfish-server/issues/1164)) ([#1460](https://github.com/varfish-org/varfish-server/issues/1460)) ([e56ad93](https://github.com/varfish-org/varfish-server/commit/e56ad937daeb043371dd0124e3b5ed233c39ebd9))
* query result sets not created on case import ([#1241](https://github.com/varfish-org/varfish-server/issues/1241)) ([#1242](https://github.com/varfish-org/varfish-server/issues/1242)) ([b5659a9](https://github.com/varfish-org/varfish-server/commit/b5659a95e0ee1df88ec243f72e545400439e125e))
* re-enable searching for cases and list in project overview ([#1004](https://github.com/varfish-org/varfish-server/issues/1004)) ([#1008](https://github.com/varfish-org/varfish-server/issues/1008)) ([8679d52](https://github.com/varfish-org/varfish-server/commit/8679d52d1b06de7f1c3effef44ccc28732093d77))
* Remove IGV prefixing ([#1284](https://github.com/varfish-org/varfish-server/issues/1284)) ([3a917fe](https://github.com/varfish-org/varfish-server/commit/3a917feb35809c7772e1d810e02fcc067046b7eb))
* replace jannovar call in file export with mehari ([#1463](https://github.com/varfish-org/varfish-server/issues/1463)) ([#1512](https://github.com/varfish-org/varfish-server/issues/1512)) ([82235b8](https://github.com/varfish-org/varfish-server/commit/82235b8dd90b590de52a9b0eb28e65b73775dbec))
* resolve issue in project QC with variant statistics API ([#1009](https://github.com/varfish-org/varfish-server/issues/1009)) ([a1188a8](https://github.com/varfish-org/varfish-server/commit/a1188a8fcd4a30e58b0385413ace01403c5013ce))
* resolve issue with sv quick preset initialization ([#1003](https://github.com/varfish-org/varfish-server/issues/1003)) ([864029a](https://github.com/varfish-org/varfish-server/commit/864029a0cb4964784326186d96ef81042ca9ee03))
* resolve pylance issue with subscription of dict ([#1187](https://github.com/varfish-org/varfish-server/issues/1187)) ([3a7fbe0](https://github.com/varfish-org/varfish-server/commit/3a7fbe0a37909f24f7ccac81aee02db8c76f9719))
* resolving issues after large-scale update ([#1107](https://github.com/varfish-org/varfish-server/issues/1107)) ([4fe2a54](https://github.com/varfish-org/varfish-server/commit/4fe2a5495291693e21ff0807143d267a3e8eafae))
* resultset store issue ([#1209](https://github.com/varfish-org/varfish-server/issues/1209)) ([e56eac7](https://github.com/varfish-org/varfish-server/commit/e56eac7d347454aaad3e7a685b3035ff7447212f))
* returning from sv details shows wrong result set ([#1438](https://github.com/varfish-org/varfish-server/issues/1438)) ([#1439](https://github.com/varfish-org/varfish-server/issues/1439)) ([1a8459d](https://github.com/varfish-org/varfish-server/commit/1a8459d925c792d3afc412f24d34ce6a27205882))
* rollback mehari call ([#1204](https://github.com/varfish-org/varfish-server/issues/1204)) ([1ce636b](https://github.com/varfish-org/varfish-server/commit/1ce636b4f776ac7d6a51e1050a1a0a1515e5d622))
* small variant and svs load all available flags and comments ([#1032](https://github.com/varfish-org/varfish-server/issues/1032)) ([#1036](https://github.com/varfish-org/varfish-server/issues/1036)) ([6bc445b](https://github.com/varfish-org/varfish-server/commit/6bc445b4e6a3d1b42f46b4afe7ea554b45296756))
* sorting broken in smallvariant results table ([#1018](https://github.com/varfish-org/varfish-server/issues/1018)) ([#1026](https://github.com/varfish-org/varfish-server/issues/1026)) ([ddae17a](https://github.com/varfish-org/varfish-server/commit/ddae17a5206c304f0fd5afad728a3e74821588d8))
* special result row set not updating when flags are updated ([#1378](https://github.com/varfish-org/varfish-server/issues/1378)) ([#1398](https://github.com/varfish-org/varfish-server/issues/1398)) ([d7ab728](https://github.com/varfish-org/varfish-server/commit/d7ab7282b5aef3ed321fa7c8d26f7794940eefd5))
* structural variant worker call ([#1203](https://github.com/varfish-org/varfish-server/issues/1203)) ([d752480](https://github.com/varfish-org/varfish-server/commit/d75248035153150656ec7c89b992d82316e010ec))
* strucvar filtration always run with grch37 ([#1271](https://github.com/varfish-org/varfish-server/issues/1271)) ([#1272](https://github.com/varfish-org/varfish-server/issues/1272)) ([c0a8fbc](https://github.com/varfish-org/varfish-server/commit/c0a8fbc665cac9078abfc3a921b6eda638f5a807))
* suppress BAM QC table if BAM stats missing ([#1213](https://github.com/varfish-org/varfish-server/issues/1213)) ([6f0cfa0](https://github.com/varfish-org/varfish-server/commit/6f0cfa0e436ac0d72530fa9e214f3cf85f4b54ce))
* sv queries submit to wrong celery worker queue ([#1052](https://github.com/varfish-org/varfish-server/issues/1052)) ([#1053](https://github.com/varfish-org/varfish-server/issues/1053)) ([e12b02d](https://github.com/varfish-org/varfish-server/commit/e12b02df82e8e2c564de0a5a2e6b17d65eceab77))
* sv results page shows previous results after sv details ([#1302](https://github.com/varfish-org/varfish-server/issues/1302)) ([#1303](https://github.com/varfish-org/varfish-server/issues/1303)) ([028e6e5](https://github.com/varfish-org/varfish-server/commit/028e6e53a4adeefae95f503583aa0ff2553352a2))
* switch case import data port setting to type integer ([#1214](https://github.com/varfish-org/varfish-server/issues/1214)) ([ac9bb76](https://github.com/varfish-org/varfish-server/commit/ac9bb7663e7401b25688274a46bdab16a123d481))
* table in default sorting after returning from details ([#1109](https://github.com/varfish-org/varfish-server/issues/1109)) ([#1110](https://github.com/varfish-org/varfish-server/issues/1110)) ([7b346d4](https://github.com/varfish-org/varfish-server/commit/7b346d450cd62487fcdd388bbd81943b3348cd20))
* table sorting on variants result page ([#1128](https://github.com/varfish-org/varfish-server/issues/1128)) ([1f3e4a2](https://github.com/varfish-org/varfish-server/commit/1f3e4a25d424674b9932913aa37a4d408622eb45))
* table sorting settings not preserved ([#1212](https://github.com/varfish-org/varfish-server/issues/1212)) ([0157ea1](https://github.com/varfish-org/varfish-server/commit/0157ea118b361734d54e35d49ef417de2d45d07b))
* timing issue when initializing pinia ([#1374](https://github.com/varfish-org/varfish-server/issues/1374)) ([64c99e6](https://github.com/varfish-org/varfish-server/commit/64c99e65f17770ec0f0427dfe406867af2a983e4))
* ugprade rfl to adjust to latest annonars and ClinVar XML changes ([#1678](https://github.com/varfish-org/varfish-server/issues/1678)) ([#1679](https://github.com/varfish-org/varfish-server/issues/1679)) ([e209961](https://github.com/varfish-org/varfish-server/commit/e209961894c7608558bbb6a9deb8b1f4d2dcedfc))
* update reev frontend lib for mt igv issue ([#1575](https://github.com/varfish-org/varfish-server/issues/1575)) ([#1576](https://github.com/varfish-org/varfish-server/issues/1576)) ([eca30d3](https://github.com/varfish-org/varfish-server/commit/eca30d3a4a4077f866a005e2dde8858bb453c4cf))
* updated pipfile lock ([#1210](https://github.com/varfish-org/varfish-server/issues/1210)) ([6ab8ff5](https://github.com/varfish-org/varfish-server/commit/6ab8ff5a358e32510c6a02365ac5dcc7dcfb10cb))
* updating Pipfile.lock ([#1054](https://github.com/varfish-org/varfish-server/issues/1054)) ([#1055](https://github.com/varfish-org/varfish-server/issues/1055)) ([fe64118](https://github.com/varfish-org/varfish-server/commit/fe6411893bbd4e063d93388ffbea03550fed15da))
* value in exon max dist prevents submitting query ([#993](https://github.com/varfish-org/varfish-server/issues/993)) ([#1005](https://github.com/varfish-org/varfish-server/issues/1005)) ([682a4c6](https://github.com/varfish-org/varfish-server/commit/682a4c61b7d1440018bb08344c85b4e29dfa096e))
* variant details not working for grch38 ([#1509](https://github.com/varfish-org/varfish-server/issues/1509)) ([#1524](https://github.com/varfish-org/varfish-server/issues/1524)) ([efeba9f](https://github.com/varfish-org/varfish-server/commit/efeba9ff2d11914d898c264e698fd0bbdee23e88))
* variant icons leads to wrong postion on variant details page ([#1315](https://github.com/varfish-org/varfish-server/issues/1315)) ([#1465](https://github.com/varfish-org/varfish-server/issues/1465)) ([9d3d83b](https://github.com/varfish-org/varfish-server/commit/9d3d83b55ff562d0e6cb88740e545bf42ec58e91))
* whole transcript preset should include non coding transcripts ([#1044](https://github.com/varfish-org/varfish-server/issues/1044)) ([#1071](https://github.com/varfish-org/varfish-server/issues/1071)) ([36e8055](https://github.com/varfish-org/varfish-server/commit/36e80553873bf80ec87d2590290b4fed47bf3594))
* wrong genome build for igv visualization of sv ([#1511](https://github.com/varfish-org/varfish-server/issues/1511)) ([#1558](https://github.com/varfish-org/varfish-server/issues/1558)) ([6b1d6c9](https://github.com/varfish-org/varfish-server/commit/6b1d6c957222a5f26ff8924ca5a4fd8661ade8c9))
* xlsx file export issues ([#1504](https://github.com/varfish-org/varfish-server/issues/1504)) ([#1505](https://github.com/varfish-org/varfish-server/issues/1505)) ([145e8b4](https://github.com/varfish-org/varfish-server/commit/145e8b4c112c71f902e1b2735c3ff4cf2a97c24b))


### Documentation

* fixing readthedocs documentation ([#1317](https://github.com/varfish-org/varfish-server/issues/1317)) ([575a946](https://github.com/varfish-org/varfish-server/commit/575a946d1ae17da12552b873240304b2fde2b3f1))
* moving out dev docs ([#1698](https://github.com/varfish-org/varfish-server/issues/1698)) ([#1704](https://github.com/varfish-org/varfish-server/issues/1704)) ([b462b68](https://github.com/varfish-org/varfish-server/commit/b462b689f6df2252ab55ff89b20c8df1a54f7996))

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
