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

## [1.3.2](https://github.com/varfish-org/varfish-server/compare/v1.3.1...v1.3.2) (2025-12-02)


### Bug Fixes

* broken sv region filter ([#2492](https://github.com/varfish-org/varfish-server/issues/2492)) ([a1a3ab2](https://github.com/varfish-org/varfish-server/commit/a1a3ab2ad317d99f32ecef2624e83c6a5802bba1))
* preset sets of all projects shouldn't be selectable for a case ([#2491](https://github.com/varfish-org/varfish-server/issues/2491)) ([1487b25](https://github.com/varfish-org/varfish-server/commit/1487b2508b8f6490d4f40374df4c7b7b15f1814b))
* sv flag coloring in results missing ([#2487](https://github.com/varfish-org/varfish-server/issues/2487)) ([78c2c52](https://github.com/varfish-org/varfish-server/commit/78c2c529a4eefd91cf3cba15307a1cab4f55af00))

## [1.3.1](https://github.com/varfish-org/varfish-server/compare/v1.3.0...v1.3.1) (2025-12-01)


### Bug Fixes

* CSP whitelist ([#2478](https://github.com/varfish-org/varfish-server/issues/2478)) ([ba9cc8f](https://github.com/varfish-org/varfish-server/commit/ba9cc8f9f673bc399e02278f597d967fcfd8b0e9))
* singleton might cause wrong inheritance preset ([#2470](https://github.com/varfish-org/varfish-server/issues/2470)) ([dbde3a0](https://github.com/varfish-org/varfish-server/commit/dbde3a01400ae19f5b637cf265e819aef6847fda))
* versioning display in footer ([#2472](https://github.com/varfish-org/varfish-server/issues/2472)) ([d94c364](https://github.com/varfish-org/varfish-server/commit/d94c3647ca49f42c8752760b4c206bd759b9cfc6))

## [1.3.0](https://github.com/varfish-org/varfish-server/compare/varfish-server-v1.2.3...varfish-server-v1.3.0) (2025-11-20)


### Features

* add case status partially-solved ([#2179](https://github.com/varfish-org/varfish-server/issues/2179)) ([#2331](https://github.com/varfish-org/varfish-server/issues/2331)) ([37a4008](https://github.com/varfish-org/varfish-server/commit/37a40087b4b3bc758ab293753aa93ec6235e0d8c))
* add manage.py initdev command ([#1767](https://github.com/varfish-org/varfish-server/issues/1767)) ([#1768](https://github.com/varfish-org/varfish-server/issues/1768)) ([f249d93](https://github.com/varfish-org/varfish-server/commit/f249d9390a1138046eb41129564557c347122b43))
* add optional integration of GestaltMatcher/PEDIA ([#399](https://github.com/varfish-org/varfish-server/issues/399), [#1125](https://github.com/varfish-org/varfish-server/issues/1125)) ([#1249](https://github.com/varfish-org/varfish-server/issues/1249)) ([6f695ec](https://github.com/varfish-org/varfish-server/commit/6f695ecbdef7ff6e1f96be3bab57b31394b33622))
* add runtask management command ([#2044](https://github.com/varfish-org/varfish-server/issues/2044)) ([#2045](https://github.com/varfish-org/varfish-server/issues/2045)) ([67f67c7](https://github.com/varfish-org/varfish-server/commit/67f67c768057404d6442638d5e8667e032cc81da))
* add strucvars data to initdev ([#2071](https://github.com/varfish-org/varfish-server/issues/2071)) ([#2072](https://github.com/varfish-org/varfish-server/issues/2072)) ([6ab216a](https://github.com/varfish-org/varfish-server/commit/6ab216a0e2a9eb4a1768d8f836a7125a25113fa2))
* added command to transfer presets, also between instances ([#2383](https://github.com/varfish-org/varfish-server/issues/2383)) ([b37641e](https://github.com/varfish-org/varfish-server/commit/b37641e8b54a58bed98fa5deb11d83ba5d8859be))
* adding cases_analysis module ([#1735](https://github.com/varfish-org/varfish-server/issues/1735)) ([#1739](https://github.com/varfish-org/varfish-server/issues/1739)) ([7ac94eb](https://github.com/varfish-org/varfish-server/commit/7ac94eb9c4406fc0e4ef98a6fa39dcf2b9e933eb))
* adding seqvars module ([#1737](https://github.com/varfish-org/varfish-server/issues/1737)) ([#1761](https://github.com/varfish-org/varfish-server/issues/1761)) ([4bab348](https://github.com/varfish-org/varfish-server/commit/4bab3481644875ae187c091e8438d3020b54f5ba))
* bump reev-frontend-lib version for mehari api calls ([#2387](https://github.com/varfish-org/varfish-server/issues/2387)) ([5bc10c3](https://github.com/varfish-org/varfish-server/commit/5bc10c37ce264387c8105af40e30ce0ecaf40fc6))
* command to delete invalid queries with invalid settings ([#1807](https://github.com/varfish-org/varfish-server/issues/1807)) ([#1855](https://github.com/varfish-org/varfish-server/issues/1855)) ([9b7f085](https://github.com/varfish-org/varfish-server/commit/9b7f085e711e8d75d06727b686f42599c799fca8))
* conversion from clinvar JSONL to legacy clinvar table ([#1963](https://github.com/varfish-org/varfish-server/issues/1963)) ([#1974](https://github.com/varfish-org/varfish-server/issues/1974)) ([b05a898](https://github.com/varfish-org/varfish-server/commit/b05a8989415ae1abc01c3d961c218b8612d9cc74))
* copy preset sets from one project to another ([#2217](https://github.com/varfish-org/varfish-server/issues/2217)) ([#2218](https://github.com/varfish-org/varfish-server/issues/2218)) ([5a036c6](https://github.com/varfish-org/varfish-server/commit/5a036c6ccaabeed99db5b8c7f40f453fec95edc0))
* create query from presets prepared query ([#1919](https://github.com/varfish-org/varfish-server/issues/1919)) ([d87b225](https://github.com/varfish-org/varfish-server/commit/d87b2252b8670690b8b4116f6bd9dfabe2d0b417))
* delete clinvar_export app ([#1664](https://github.com/varfish-org/varfish-server/issues/1664)) ([#1762](https://github.com/varfish-org/varfish-server/issues/1762)) ([e75275c](https://github.com/varfish-org/varfish-server/commit/e75275c48bd1ac1ae127ef8d5481800c75d38617))
* display seqvars query execution results in UI ([#1952](https://github.com/varfish-org/varfish-server/issues/1952)) ([#1957](https://github.com/varfish-org/varfish-server/issues/1957)) ([911c181](https://github.com/varfish-org/varfish-server/commit/911c18124ea49b5f82a36d77fd46875bf4ed5ead))
* enable opening variant details in separate browser tab ([#1886](https://github.com/varfish-org/varfish-server/issues/1886)) ([#1903](https://github.com/varfish-org/varfish-server/issues/1903)) ([521fcc8](https://github.com/varfish-org/varfish-server/commit/521fcc8fcc3baacfc214141c347bb43efadf57e1))
* execution of seqvar query jobs ([#1949](https://github.com/varfish-org/varfish-server/issues/1949)) ([#1950](https://github.com/varfish-org/varfish-server/issues/1950)) ([9ed31a8](https://github.com/varfish-org/varfish-server/commit/9ed31a86cf328c3c6554330c715f13f476a5b509))
* extend initdev command to also setup case import ([#1942](https://github.com/varfish-org/varfish-server/issues/1942)) ([#1948](https://github.com/varfish-org/varfish-server/issues/1948)) ([d958421](https://github.com/varfish-org/varfish-server/commit/d9584211d8b71c8ac8f6ff90f9e141ac1669ef49))
* extend models and API schema for worker output ([#1872](https://github.com/varfish-org/varfish-server/issues/1872)) ([#1873](https://github.com/varfish-org/varfish-server/issues/1873)) ([a6dcac2](https://github.com/varfish-org/varfish-server/commit/a6dcac24fd94c71b662964d926708e22b01d34d4))
* further integration of seqvars query UI ([#1917](https://github.com/varfish-org/varfish-server/issues/1917)) ([b1678ce](https://github.com/varfish-org/varfish-server/commit/b1678cea18788bd62db193aa49e1ef85ce5ea718))
* genotype choice enabled and non_het ([#1815](https://github.com/varfish-org/varfish-server/issues/1815)) ([#1817](https://github.com/varfish-org/varfish-server/issues/1817)) ([06a7dd0](https://github.com/varfish-org/varfish-server/commit/06a7dd07d0b6971e1169309c77e037be2fdbc015))
* hemizygous count is not displayed in varfish variant detail ([#1](https://github.com/varfish-org/varfish-server/issues/1)… ([#1860](https://github.com/varfish-org/varfish-server/issues/1860)) ([066e2f9](https://github.com/varfish-org/varfish-server/commit/066e2f9a4eae4f71a9211d1fa8be7ac7f7a948b8))
* impact not updated when quick presets are updated ([#2014](https://github.com/varfish-org/varfish-server/issues/2014)) ([#2027](https://github.com/varfish-org/varfish-server/issues/2027)) ([edcc966](https://github.com/varfish-org/varfish-server/commit/edcc966b01a6c97ebe0112f1f055b24ab84694d2))
* implement seqvars presets editor ([#1763](https://github.com/varfish-org/varfish-server/issues/1763)) ([#1857](https://github.com/varfish-org/varfish-server/issues/1857)) ([98421e9](https://github.com/varfish-org/varfish-server/commit/98421e9988ecb817e37f1c4ec26aaf2db15c4bcd))
* implement seqvars query results storage ([#1951](https://github.com/varfish-org/varfish-server/issues/1951)) ([#1953](https://github.com/varfish-org/varfish-server/issues/1953)) ([6ad33c5](https://github.com/varfish-org/varfish-server/commit/6ad33c5480d296f8f946fbeeb1902d4374b63342))
* improving folding of left menu ([#1877](https://github.com/varfish-org/varfish-server/issues/1877)) ([#1881](https://github.com/varfish-org/varfish-server/issues/1881)) ([7591170](https://github.com/varfish-org/varfish-server/commit/75911704a6746cb29ceffbae35a7c5c467089883))
* initial set of seqvar stores based on code generated from OpenAPI ([#1765](https://github.com/varfish-org/varfish-server/issues/1765)) ([#1769](https://github.com/varfish-org/varfish-server/issues/1769)) ([ae9c1f3](https://github.com/varfish-org/varfish-server/commit/ae9c1f3fe36f1b1da2b3b7a29c0e9af2132da97d))
* initial version of seqvar filtration screens in storybook ([#1745](https://github.com/varfish-org/varfish-server/issues/1745)) ([c73ad2b](https://github.com/varfish-org/varfish-server/commit/c73ad2b3d7b297045a82b5d2307ed92ed7f81479))
* integrate seqvars inhouse rocksdb in worker call ([#2069](https://github.com/varfish-org/varfish-server/issues/2069)) ([#2070](https://github.com/varfish-org/varfish-server/issues/2070)) ([0d5e380](https://github.com/varfish-org/varfish-server/commit/0d5e380336644b66781310cc945ef4ac826291fa))
* integration of seqvars query interface (no 2) ([#1891](https://github.com/varfish-org/varfish-server/issues/1891)) ([9f088b7](https://github.com/varfish-org/varfish-server/commit/9f088b77bcc1713e02cf921016cf8e20a58a02fd))
* make omim search case insensitive ([#1788](https://github.com/varfish-org/varfish-server/issues/1788)) ([#1806](https://github.com/varfish-org/varfish-server/issues/1806)) ([95bb7ce](https://github.com/varfish-org/varfish-server/commit/95bb7ce958fc34b64ed9b4ff5f4a35862c2ddbfc))
* make Vue3 frontend a true SPA ([#1770](https://github.com/varfish-org/varfish-server/issues/1770)) ([#1771](https://github.com/varfish-org/varfish-server/issues/1771)) ([d65e2a6](https://github.com/varfish-org/varfish-server/commit/d65e2a68b42d80f50542eaa368b401fbb8ce2eaa))
* mark queries as started from the UI ([#1939](https://github.com/varfish-org/varfish-server/issues/1939)) ([#1941](https://github.com/varfish-org/varfish-server/issues/1941)) ([1a1a7ff](https://github.com/varfish-org/varfish-server/commit/1a1a7ffbf5655f234d2db08035c26460824c2e62))
* migrate cases import rest api to viewset ([#1947](https://github.com/varfish-org/varfish-server/issues/1947)) ([#1962](https://github.com/varfish-org/varfish-server/issues/1962)) ([80b0423](https://github.com/varfish-org/varfish-server/commit/80b0423b707f728d0ac90a20257e0373cf379f9e))
* move to single side bar design for seqvars query ([#2095](https://github.com/varfish-org/varfish-server/issues/2095)) ([#2096](https://github.com/varfish-org/varfish-server/issues/2096)) ([b3045b7](https://github.com/varfish-org/varfish-server/commit/b3045b772b38150941840136f68c4a2da3c1b941))
* new mehari effects april 2025 ([#2312](https://github.com/varfish-org/varfish-server/issues/2312)) ([#2376](https://github.com/varfish-org/varfish-server/issues/2376)) ([7e5aba0](https://github.com/varfish-org/varfish-server/commit/7e5aba0b74a587deed1e3f83020e601d4523e14b))
* phenotype&pathogenicity prio filter ([#1830](https://github.com/varfish-org/varfish-server/issues/1830)) ([1fa8a24](https://github.com/varfish-org/varfish-server/commit/1fa8a2469f0debb9b71018bc2e1bf852edb35407))
* polish query results table ([#2052](https://github.com/varfish-org/varfish-server/issues/2052)) ([a02cf55](https://github.com/varfish-org/varfish-server/commit/a02cf55f7a8ae4a912491575c87d6e84ae6556ca))
* pulling gnomad constraints for result table from annonars ([#2381](https://github.com/varfish-org/varfish-server/issues/2381)) ([3329cf5](https://github.com/varfish-org/varfish-server/commit/3329cf5ee8ea73460130a14347fa701905877eed))
* query presets in svs not loaded ([#2264](https://github.com/varfish-org/varfish-server/issues/2264)) ([#2265](https://github.com/varfish-org/varfish-server/issues/2265)) ([808ca12](https://github.com/varfish-org/varfish-server/commit/808ca123f2d2fa42c99cc41366e0646c71e523b6))
* quick preset editor values must be set on creation ([#2028](https://github.com/varfish-org/varfish-server/issues/2028)) ([#2039](https://github.com/varfish-org/varfish-server/issues/2039)) ([b945adb](https://github.com/varfish-org/varfish-server/commit/b945adbc3fa08f581a9bb3f5070a74c1ab7d0008))
* refine seqvars result table display ([#2017](https://github.com/varfish-org/varfish-server/issues/2017)) ([#2046](https://github.com/varfish-org/varfish-server/issues/2046)) ([01a9a89](https://github.com/varfish-org/varfish-server/commit/01a9a89825e187b2f944cab3ae5f9ceb9d2bde1a))
* removal of dependencies to geneinfo app ([#1635](https://github.com/varfish-org/varfish-server/issues/1635)) ([#1719](https://github.com/varfish-org/varfish-server/issues/1719)) ([48c1728](https://github.com/varfish-org/varfish-server/commit/48c17282b3fdce55cddccf0939655ebfe75104ab))
* remove obsolete models in queries ([#2371](https://github.com/varfish-org/varfish-server/issues/2371)) ([#2372](https://github.com/varfish-org/varfish-server/issues/2372)) ([283cb8f](https://github.com/varfish-org/varfish-server/commit/283cb8fa6140e1b9ed36efa4eee17dddc3c74267))
* searching for cases is painful ([#1645](https://github.com/varfish-org/varfish-server/issues/1645)) ([#1802](https://github.com/varfish-org/varfish-server/issues/1802)) ([5064a27](https://github.com/varfish-org/varfish-server/commit/5064a27ed8547e25d2529ad7e3c4b200fa4ceada))
* seqvar item modified & revert  ([#1818](https://github.com/varfish-org/varfish-server/issues/1818)) ([c885421](https://github.com/varfish-org/varfish-server/commit/c8854214fe15c0c97fa6bc34230eb2f3272883eb))
* seqvar panels ([#1883](https://github.com/varfish-org/varfish-server/issues/1883)) ([9d18422](https://github.com/varfish-org/varfish-server/commit/9d18422001108e7fc70bf65c5f5dcc9177e344bd))
* seqvar quality, clinvar & locus filters ([#1856](https://github.com/varfish-org/varfish-server/issues/1856)) ([cf00085](https://github.com/varfish-org/varfish-server/commit/cf00085630a4e59c6481b349a1a5aaa1e45ae78b))
* seqvars data-table ([#1870](https://github.com/varfish-org/varfish-server/issues/1870)) ([d5cb17b](https://github.com/varfish-org/varfish-server/commit/d5cb17bf7f6f87333c15c477d6ce99f9d43e0684))
* seqvars effects filter ([#1833](https://github.com/varfish-org/varfish-server/issues/1833)) ([38febb1](https://github.com/varfish-org/varfish-server/commit/38febb1c55df3243054fbeb45b34ab2cc132e1eb))
* seqvars summary item show modified + revert ([#1890](https://github.com/varfish-org/varfish-server/issues/1890)) ([5f1e1fd](https://github.com/varfish-org/varfish-server/commit/5f1e1fdbcefabcb08497524b097e899af1b5f6f5))
* set order of quick presets in dropdown ([#1479](https://github.com/varfish-org/varfish-server/issues/1479)) ([#1794](https://github.com/varfish-org/varfish-server/issues/1794)) ([5d074a5](https://github.com/varfish-org/varfish-server/commit/5d074a59a5478a7da3cf7d6f065bfede5dd55bdc))
* split frequency type further ([#1784](https://github.com/varfish-org/varfish-server/issues/1784)) ([3c325fe](https://github.com/varfish-org/varfish-server/commit/3c325fe892edde0a37da9030418392018439c93b))
* splitting recessive_parent into recessive_{father,mother} ([#1867](https://github.com/varfish-org/varfish-server/issues/1867)) ([#1868](https://github.com/varfish-org/varfish-server/issues/1868)) ([c5fb09b](https://github.com/varfish-org/varfish-server/commit/c5fb09b96b1c2842469abb4b39e2e30947d06404))
* start integrating seqvars filtration with frontend ([#1882](https://github.com/varfish-org/varfish-server/issues/1882)) ([#1889](https://github.com/varfish-org/varfish-server/issues/1889)) ([5199606](https://github.com/varfish-org/varfish-server/commit/5199606145486b4d632195f0160fa27295fc4985))
* store collapsible state in local storage ([#2043](https://github.com/varfish-org/varfish-server/issues/2043)) ([#2047](https://github.com/varfish-org/varfish-server/issues/2047)) ([f15205c](https://github.com/varfish-org/varfish-server/commit/f15205c92537ea1826bc67848ecc7eb08da90395))
* support for more annotations ([#2041](https://github.com/varfish-org/varfish-server/issues/2041)) ([#2048](https://github.com/varfish-org/varfish-server/issues/2048)) ([7fea8c7](https://github.com/varfish-org/varfish-server/commit/7fea8c7ba654bda831f52185e5d40523a57b72d0))
* switching to builtin OpenAPI generation from drf ([#1734](https://github.com/varfish-org/varfish-server/issues/1734)) ([9561fb4](https://github.com/varfish-org/varfish-server/commit/9561fb4d52f1bde2225fb4c333cf7195e230b5c6))
* update reev - geneinfo possibly lost ([#2346](https://github.com/varfish-org/varfish-server/issues/2346)) ([051fc2b](https://github.com/varfish-org/varfish-server/commit/051fc2b31e23444306be91ae1f0967efb3bf06d8))
* upgrade to sodar core v1 ([#1973](https://github.com/varfish-org/varfish-server/issues/1973)) ([#2010](https://github.com/varfish-org/varfish-server/issues/2010)) ([f112861](https://github.com/varfish-org/varfish-server/commit/f11286117d99da5438dab26d5dea1d5715ecedc7))


### Bug Fixes

* add docx export button for custom query presets ([#2427](https://github.com/varfish-org/varfish-server/issues/2427)) ([23fa8dc](https://github.com/varfish-org/varfish-server/commit/23fa8dc450d119ec57e34c1726b13edbd5430c92))
* add missing consequences ([#2260](https://github.com/varfish-org/varfish-server/issues/2260)) ([#2261](https://github.com/varfish-org/varfish-server/issues/2261)) ([67ca36d](https://github.com/varfish-org/varfish-server/commit/67ca36da390e5a1553e03ca8b563f341a7f29fd2))
* added presets to docx converter ([#2425](https://github.com/varfish-org/varfish-server/issues/2425)) ([2c23a51](https://github.com/varfish-org/varfish-server/commit/2c23a51a0dc995fc3cdb297dbfbd37a41f8afcd6))
* added trailing slash in api to enable file export again ([#2382](https://github.com/varfish-org/varfish-server/issues/2382)) ([5e5876c](https://github.com/varfish-org/varfish-server/commit/5e5876c2260a894999adaaf8778a073ed4826bac))
* adding missing references to category presets ([#1793](https://github.com/varfish-org/varfish-server/issues/1793)) ([ec715ce](https://github.com/varfish-org/varfish-server/commit/ec715cec29deaa01a761008cd9008bdafa87dde9))
* annotated sv not listed in case annotations ([#2015](https://github.com/varfish-org/varfish-server/issues/2015)) ([#2030](https://github.com/varfish-org/varfish-server/issues/2030)) ([4dbf02b](https://github.com/varfish-org/varfish-server/commit/4dbf02bab7787ae23fd16872934d8428ea357cca))
* caller splitting for old cases ([#1741](https://github.com/varfish-org/varfish-server/issues/1741)) ([#1742](https://github.com/varfish-org/varfish-server/issues/1742)) ([a9d9416](https://github.com/varfish-org/varfish-server/commit/a9d9416fe7e230eeaa0f7fb2ff627504f8867fe0))
* case overview diseases terms input missing omim ([#1759](https://github.com/varfish-org/varfish-server/issues/1759)) ([#1785](https://github.com/varfish-org/varfish-server/issues/1785)) ([9f55cd5](https://github.com/varfish-org/varfish-server/commit/9f55cd59615f3a54f6e6897d073818b2f2f64470))
* case search still broken ([#1803](https://github.com/varfish-org/varfish-server/issues/1803)) ([#1804](https://github.com/varfish-org/varfish-server/issues/1804)) ([888a952](https://github.com/varfish-org/varfish-server/commit/888a952bd5b48a31cbf7fbdbf40befd3b826e64d))
* clicking variant modal sidebar does not work ([#1849](https://github.com/varfish-org/varfish-server/issues/1849)) ([#1869](https://github.com/varfish-org/varfish-server/issues/1869)) ([c187a1d](https://github.com/varfish-org/varfish-server/commit/c187a1dd369a98a673d9794173ec7025d66f1a4a))
* clicking variant twice fails loading the variant details ([#1940](https://github.com/varfish-org/varfish-server/issues/1940)) ([#1975](https://github.com/varfish-org/varfish-server/issues/1975)) ([781c82b](https://github.com/varfish-org/varfish-server/commit/781c82b4e03f5f11a7ceacfdae8eed12f4f6aa1c))
* clinvar paranoid checkbox has no effect ([#2392](https://github.com/varfish-org/varfish-server/issues/2392)) ([7b7369a](https://github.com/varfish-org/varfish-server/commit/7b7369ad2ca5246c40b8beabb519113a2213a7ec))
* cloning query presets results in blank preset ([#1837](https://github.com/varfish-org/varfish-server/issues/1837)) ([#1874](https://github.com/varfish-org/varfish-server/issues/1874)) ([e555686](https://github.com/varfish-org/varfish-server/commit/e555686f2b6fc962b92fd0114f290e0957fdafa3))
* coerce FORMAT/cn to int when writing SV VCF ([#1743](https://github.com/varfish-org/varfish-server/issues/1743)) ([#1744](https://github.com/varfish-org/varfish-server/issues/1744)) ([22ed8bd](https://github.com/varfish-org/varfish-server/commit/22ed8bd97bccdf9d0a2a1b821e004fae54dd6e4d))
* collapsable side menu icon not intuitive ([#1875](https://github.com/varfish-org/varfish-server/issues/1875)) ([#1876](https://github.com/varfish-org/varfish-server/issues/1876)) ([b08dbb2](https://github.com/varfish-org/varfish-server/commit/b08dbb243c0d10e39d867c5d790858240ec42f6a))
* complexity setting for filters missing in new interface ([#1853](https://github.com/varfish-org/varfish-server/issues/1853)) ([#1859](https://github.com/varfish-org/varfish-server/issues/1859)) ([44edb7e](https://github.com/varfish-org/varfish-server/commit/44edb7ec5a97da9b40442c3425287043511540e1))
* devtools in seqvar query ([#2097](https://github.com/varfish-org/varfish-server/issues/2097)) ([#2098](https://github.com/varfish-org/varfish-server/issues/2098)) ([58b79e8](https://github.com/varfish-org/varfish-server/commit/58b79e8c7e7a403d9628619ce64701c7b6064a99))
* display grch38 sample counts in frequency pane ([#2430](https://github.com/varfish-org/varfish-server/issues/2430)) ([#2431](https://github.com/varfish-org/varfish-server/issues/2431)) ([e514be2](https://github.com/varfish-org/varfish-server/commit/e514be236359d15e7338abc0ec8b904307476060))
* displayed pedigree in filter interface is wrong ([#2214](https://github.com/varfish-org/varfish-server/issues/2214)) ([#2216](https://github.com/varfish-org/varfish-server/issues/2216)) ([5b7f4fd](https://github.com/varfish-org/varfish-server/commit/5b7f4fdc92d8fc36db56a481432809e8b0751859))
* empty genotype data in sample cause sv query to crash ([#2201](https://github.com/varfish-org/varfish-server/issues/2201)) ([#2235](https://github.com/varfish-org/varfish-server/issues/2235)) ([56f1b4b](https://github.com/varfish-org/varfish-server/commit/56f1b4b120f3e99846000d8c71017c672b585058))
* export query settings and presets as pdf instead of docx ([#2432](https://github.com/varfish-org/varfish-server/issues/2432)) ([25f67ed](https://github.com/varfish-org/varfish-server/commit/25f67ed8be78f6a52fc537db212feed3099e1b5c))
* filter for hemizygous frequencies does not work ([#2100](https://github.com/varfish-org/varfish-server/issues/2100)) ([#2101](https://github.com/varfish-org/varfish-server/issues/2101)) ([05c1887](https://github.com/varfish-org/varfish-server/commit/05c18874a334796e90b5e52ab730fd569431cb90))
* fix server worker version ([#1909](https://github.com/varfish-org/varfish-server/issues/1909)) ([df37363](https://github.com/varfish-org/varfish-server/commit/df37363a37ef24ad14968947af6ebd61552cc80a))
* frontend build fails on machines less than 32gb ram ([#1720](https://github.com/varfish-org/varfish-server/issues/1720)) ([#1721](https://github.com/varfish-org/varfish-server/issues/1721)) ([c4ab0d8](https://github.com/varfish-org/varfish-server/commit/c4ab0d8dc082d1d82a6642bb6679eae27fd69757))
* gene variant missing in any quick preset ([#2379](https://github.com/varfish-org/varfish-server/issues/2379)) ([ceec7af](https://github.com/varfish-org/varfish-server/commit/ceec7af057fab1960e083fda6e5ba8517fbedf73))
* hpo terms not findable ([#1814](https://github.com/varfish-org/varfish-server/issues/1814)) ([#1829](https://github.com/varfish-org/varfish-server/issues/1829)) ([96ec15b](https://github.com/varfish-org/varfish-server/commit/96ec15b8c2568f28efe643bb56a25479b43c2acf))
* import fails with error 'intron_variant' ([#2203](https://github.com/varfish-org/varfish-server/issues/2203)) ([#2243](https://github.com/varfish-org/varfish-server/issues/2243)) ([073b1a5](https://github.com/varfish-org/varfish-server/commit/073b1a52b1861bb87561a52f920ccda03f401a8f))
* make filter settings easily exportable as docx ([#2418](https://github.com/varfish-org/varfish-server/issues/2418)) ([#2426](https://github.com/varfish-org/varfish-server/issues/2426)) ([15d81d8](https://github.com/varfish-org/varfish-server/commit/15d81d8648635db3b2a0b8fcc7c8a1ffd29f13a2))
* make Optional work with spectacular ([#1786](https://github.com/varfish-org/varfish-server/issues/1786)) ([d63f184](https://github.com/varfish-org/varfish-server/commit/d63f184592b13853a7ef302da342f7a4741fcc52))
* max exon dist does not consider negative distances ([#2327](https://github.com/varfish-org/varfish-server/issues/2327)) ([#2328](https://github.com/varfish-org/varfish-server/issues/2328)) ([bb38817](https://github.com/varfish-org/varfish-server/commit/bb38817a90234f07ca1611022a9acc90c5508d29))
* new effects missing in json schema ([#2275](https://github.com/varfish-org/varfish-server/issues/2275)) ([#2276](https://github.com/varfish-org/varfish-server/issues/2276)) ([1592e84](https://github.com/varfish-org/varfish-server/commit/1592e849048c5007320e0eec0f0bbcdbec007d51))
* not all variant effects in enum ([3d007c0](https://github.com/varfish-org/varfish-server/commit/3d007c0689b041d55f24f84ee18a5a065d2e669b))
* pedigree edits are not saved ([#2112](https://github.com/varfish-org/varfish-server/issues/2112)) ([#2113](https://github.com/varfish-org/varfish-server/issues/2113)) ([c80e809](https://github.com/varfish-org/varfish-server/commit/c80e809c45d57d4455d6c1e02457d317f8331575))
* preset editor does not allow empty frequency fields ([#2449](https://github.com/varfish-org/varfish-server/issues/2449)) ([#2450](https://github.com/varfish-org/varfish-server/issues/2450)) ([0685a8c](https://github.com/varfish-org/varfish-server/commit/0685a8c08a470d0ab6546200463ef18d07a4b1bd))
* properly interpret Optional[] in seqvars types and API ([#1789](https://github.com/varfish-org/varfish-server/issues/1789)) ([#1790](https://github.com/varfish-org/varfish-server/issues/1790)) ([36da785](https://github.com/varfish-org/varfish-server/commit/36da785c15798f7d8f81733b97b72832fdab9beb))
* properly representing recessive for genotypes ([#1808](https://github.com/varfish-org/varfish-server/issues/1808)) ([8dbb5fb](https://github.com/varfish-org/varfish-server/commit/8dbb5fb2b60c745d1b2d10e2733ecfea486d301e))
* pubtator store loading with missing hgnc id ([#1884](https://github.com/varfish-org/varfish-server/issues/1884)) ([#1887](https://github.com/varfish-org/varfish-server/issues/1887)) ([0dd8ea1](https://github.com/varfish-org/varfish-server/commit/0dd8ea1459a3019c9d648ff83a2be9f1e5195a5b))
* qc relatedness computation broken for grch38 ([#2428](https://github.com/varfish-org/varfish-server/issues/2428)) ([#2429](https://github.com/varfish-org/varfish-server/issues/2429)) ([20254e7](https://github.com/varfish-org/varfish-server/commit/20254e7b65541c3e80ab65eb8750e08a353606b4))
* release please workflow ([#2466](https://github.com/varfish-org/varfish-server/issues/2466)) ([169a396](https://github.com/varfish-org/varfish-server/commit/169a3969f4ba862adc79d8701c49d2b86f2239f3))
* release-please config for version file ([bd410b0](https://github.com/varfish-org/varfish-server/commit/bd410b0739902195b3745bc04c1d3b9077e3d835))
* resolve issues with initdev command ([#2051](https://github.com/varfish-org/varfish-server/issues/2051)) ([5c2cc7f](https://github.com/varfish-org/varfish-server/commit/5c2cc7f652330d52cc4eda9b5b1d130a864a8bb1))
* results table loses sorting after variant details ([#1211](https://github.com/varfish-org/varfish-server/issues/1211)) ([#1832](https://github.com/varfish-org/varfish-server/issues/1832)) ([5a0f325](https://github.com/varfish-org/varfish-server/commit/5a0f325aeaad61b32ad05d3a9d1fe97ff4051aca))
* selecting impact preset doesn't always restore selection ([#2415](https://github.com/varfish-org/varfish-server/issues/2415)) ([#2419](https://github.com/varfish-org/varfish-server/issues/2419)) ([ae00384](https://github.com/varfish-org/varfish-server/commit/ae00384fa1a2cc5a22c2dab0d16fe5e9455a9267))
* set order of quick presets in dropdown ([#1479](https://github.com/varfish-org/varfish-server/issues/1479)) ([#1838](https://github.com/varfish-org/varfish-server/issues/1838)) ([9b49acb](https://github.com/varfish-org/varfish-server/commit/9b49acbc85cd765bfb8e941454362bba34029687))
* show number of individuals accounted for the inhouse db ([#2451](https://github.com/varfish-org/varfish-server/issues/2451)) ([#2452](https://github.com/varfish-org/varfish-server/issues/2452)) ([a296860](https://github.com/varfish-org/varfish-server/commit/a29686008ea5f737c6d75b2e32c3d3b326f15f15))
* show visible response if user enters an invalid hpo term ([#1791](https://github.com/varfish-org/varfish-server/issues/1791)) ([#1819](https://github.com/varfish-org/varfish-server/issues/1819)) ([159a372](https://github.com/varfish-org/varfish-server/commit/159a372665743c5f067baf65a945c62c5a25a62a))
* sort case search results ([#1810](https://github.com/varfish-org/varfish-server/issues/1810)) ([#1812](https://github.com/varfish-org/varfish-server/issues/1812)) ([f78c351](https://github.com/varfish-org/varfish-server/commit/f78c351dbf7e8e025fbbdef149fa51f6976bedcd))
* spectacular integration with pydantic field ([#1783](https://github.com/varfish-org/varfish-server/issues/1783)) ([b1fa2b5](https://github.com/varfish-org/varfish-server/commit/b1fa2b5ce7e82202b4e605095c0a9a9238d45b84))
* store query presets factory defaults in db ([#1920](https://github.com/varfish-org/varfish-server/issues/1920)) ([#2067](https://github.com/varfish-org/varfish-server/issues/2067)) ([65cbca2](https://github.com/varfish-org/varfish-server/commit/65cbca27b9467954b4522309edbf548f0752f3e8))
* strucvar detail lists all comments from project ([#1960](https://github.com/varfish-org/varfish-server/issues/1960)) ([#1961](https://github.com/varfish-org/varfish-server/issues/1961)) ([baa04cd](https://github.com/varfish-org/varfish-server/commit/baa04cd4464a92bbd89553ea413965240257e171))
* sv filter results display hom for ./. genotypes ([#2401](https://github.com/varfish-org/varfish-server/issues/2401)) ([#2402](https://github.com/varfish-org/varfish-server/issues/2402)) ([1ca31ed](https://github.com/varfish-org/varfish-server/commit/1ca31edb49c6e3025f6738068cc5fc1937ae0fba))
* sv x-recessive preset filters whole genome ([#2416](https://github.com/varfish-org/varfish-server/issues/2416)) ([#2417](https://github.com/varfish-org/varfish-server/issues/2417)) ([a90c60e](https://github.com/varfish-org/varfish-server/commit/a90c60e7811e5d1214da7c584a154ef4951c1e76))
* table settings lost when returning from variant details 2 ([#1211](https://github.com/varfish-org/varfish-server/issues/1211)) ([#1839](https://github.com/varfish-org/varfish-server/issues/1839)) ([122a416](https://github.com/varfish-org/varfish-server/commit/122a416801f3c873ec672307bf3015ec1889470a))
* update reev frontend lib ([#1958](https://github.com/varfish-org/varfish-server/issues/1958)) ([#1959](https://github.com/varfish-org/varfish-server/issues/1959)) ([ada879a](https://github.com/varfish-org/varfish-server/commit/ada879a999ce451a5fcf575142d83851967f0772))
* update server worker to version 0.17.1 ([#2249](https://github.com/varfish-org/varfish-server/issues/2249)) ([#2250](https://github.com/varfish-org/varfish-server/issues/2250)) ([29c005d](https://github.com/varfish-org/varfish-server/commit/29c005d22316fb8873b55f1479709ec0c4778488))
* updating mehari and viguno api urls ([#2386](https://github.com/varfish-org/varfish-server/issues/2386)) ([6f1a861](https://github.com/varfish-org/varfish-server/commit/6f1a861f9c0f9fec3e7f7226635b0d5be003073e))
* updating reev lib for mehari openapi schema ([#2405](https://github.com/varfish-org/varfish-server/issues/2405)) ([79ba808](https://github.com/varfish-org/varfish-server/commit/79ba808e4c5dea60bd354d6436692a2781fa95fe))
* use Python 3.10 on Ubuntu noble in Docker ([#2073](https://github.com/varfish-org/varfish-server/issues/2073)) ([#2074](https://github.com/varfish-org/varfish-server/issues/2074)) ([0b8ee87](https://github.com/varfish-org/varfish-server/commit/0b8ee8741d61cbe630bec178549d7fdc06563b89))
* variant details loading broken ([#1904](https://github.com/varfish-org/varfish-server/issues/1904)) ([#1905](https://github.com/varfish-org/varfish-server/issues/1905)) ([3a4a3bf](https://github.com/varfish-org/varfish-server/commit/3a4a3bf30aa4aa90129089234016e66b403f982a))
* variant modal shifts around during loading ([#1850](https://github.com/varfish-org/varfish-server/issues/1850)) ([#1871](https://github.com/varfish-org/varfish-server/issues/1871)) ([b64a365](https://github.com/varfish-org/varfish-server/commit/b64a3659e4cb6c4841697a1a88d1c26cae9075d1))
* variantvalidator api does not work ([#1851](https://github.com/varfish-org/varfish-server/issues/1851)) ([#1858](https://github.com/varfish-org/varfish-server/issues/1858)) ([41e4284](https://github.com/varfish-org/varfish-server/commit/41e42843e9c6220d0163cc0c8d6392b42b907bf4))
* variantvalidator in variant details view broken ([#1747](https://github.com/varfish-org/varfish-server/issues/1747)) ([#1787](https://github.com/varfish-org/varfish-server/issues/1787)) ([69bae65](https://github.com/varfish-org/varfish-server/commit/69bae65db608e2d3cdc1d75e3cad72918214c205))

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
