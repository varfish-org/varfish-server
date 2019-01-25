SHELL = /bin/bash
MANAGE = time python manage.py
VARFISH_ANNO = /vol/local/data/varfish-anno
DB_PATH = $(VARFISH_ANNO)/databases
# those variables have to be passed when importing a case, e.g. via commanline
UUID =
CASE =
VARIANTS_PATH =
GENOTYPES_PATH =
PED_PATH =


.PHONY: $(SMALLVARIANTS) $(CASES) $(ANNOTATIONS) $(DB_PATH)/kegg/genetokegg.fk.tsv

black:
	black -l 100 bgjobs variants importer annotation geneinfo hgmd docs_manual var_stats_qc

serve:
	$(MANAGE) runserver

serve_public:
	$(MANAGE) runserver 0.0.0.0:8000

flushdb:
	$(MANAGE) flush

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

shell:
	$(MANAGE) shell

celery:
	celery worker -A config.celery_app -l info --concurrency=4 --beat

# cases have to be imported individualy
import_case: $(VARIANTS_PATH) $(GENOTYPES_PATH) $(PED_PATH)
	$(MANAGE) import_case \
		--project-uuid $(UUID) \
		--case-name $(CASE) \
		--index-name $(INDEX) \
		--path-variants $(VARIANTS_PATH) \
		--path-genotypes $(GENOTYPE_PATH) \
		--path-ped $(PED_PATH)

import_dbsnp: $(wildcard $(DB_PATH)/dbsnp/*.tsv)
	$(MANAGE) import --path $< --database dbsnp --release "b151"

import_exac: $(wildcard $(DB_PATH)/exac/*.tsv)
	$(MANAGE) import --path $< --database exac --release "r0.3.1"

import_gnomadexomes: $(wildcard $(DB_PATH)/gnomad_exomes/*.tsv)
	$(MANAGE) import --path $< --database gnomadexomes --release "r2.0.2"

import_gnomadgenomes: $(wildcard $(DB_PATH)/gnomad_genomes/*.tsv)
	$(MANAGE) import --path $< --database gnomadgenomes --release "r2.0.2"

import_thousandgenomes: $(wildcard $(DB_PATH)/thousand_genomes/*.tsv)
	$(MANAGE) import --path $< --database thousandgenomes --release "xxx"

import_hgnc: $(wildcard $(DB_PATH)/hgnc/*.tsv)
	$(MANAGE) import --path $< --database hgnc --release "2018-07-19"

import_hpo: $(wildcard $(DB_PATH)/hpo/*.tsv)
	$(MANAGE) import --path $< --database hpo --release "2018-07-19"

import_omim: $(wildcard $(DB_PATH)/omim/*.tsv)
	$(MANAGE) import --path $< --database omim --release "2018-07-19"

import_kegginfo: $(DB_PATH)/kegg/kegginfo.tsv
	$(MANAGE) import --path $< --database kegginfo --release "2018-08-14"

$(DB_PATH)/kegg/ensembltokegg.fk.tsv $(DB_PATH)/kegg/refseqtokegg.fk.tsv: import_kegginfo
	$(MANAGE) replace_fk_in_tsv --out $@ --in $(patsubst %.fk.tsv,%.tsv,$@) --table kegginfo --field kegg_id

import_kegg: import_ensembltokegg import_refseqtokegg

import_ensembltokegg: $(DB_PATH)/kegg/ensembltokegg.fk.tsv
	$(MANAGE) import --path $< --database ensembltokegg --release "2018-08-14"

import_refseqtokegg: $(DB_PATH)/kegg/refseqtokegg.fk.tsv
	$(MANAGE) import --path $< --database refseqtokegg --release "2018-08-14"

import_clinvar_multi: $(wildcard $(DB_PATH)/clinvar/*.multi.*.tsv)
	$(MANAGE) import --path $< --database clinvar --release "2018-11-12"

import_clinvar_single: $(wildcard $(DB_PATH)/clinvar/*.single.*.tsv)
	$(MANAGE) import --path $< --database clinvar --release "2018-11-12"

import_knowngeneaa: $(wildcard $(DB_PATH)/knowngeneaa/*.tsv)
	$(MANAGE) import --path $< --database knowngeneaa --release "2018-09-24"

import_hgmd_public: $(DB_PATH)/hgmd/hgmd_public.bed
	$(MANAGE) import --path $< --database hgmd_public --release "2018-11-16"

import_clinvar: import_clinvar_single import_clinvar_multi

import: import_exac import_dbsnp import_gnomadexomes import_hgnc import_hpo import_omim import_kegg import_clinvar import_knowngeneaa import_hgmd_public

# Remember to execute 'python manage.py collectstatic' before executing tests the first time
test:
	coverage run manage.py test -v2 --settings=config.settings.test
	coverage report
