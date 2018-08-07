SHELL := /bin/bash
MANAGE := time python manage.py
SAMPLES := $(wildcard ../tenderloin/vcf/as_tsv/*.main.header.tsv)
PEDIGREES := $(wildcard ../tenderloin/pedigree/*.header.tsv)
ANNOTATIONS := $(wildcard ../tenderloin/vcf/as_tsv/*.annotation.header.tsv)

.PHONY: $(SAMPLES) $(PEDIGREES) $(ANNOTATIONS)

serve:
	$(MANAGE) runserver

flushdb:
	$(MANAGE) flush

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

shell:
	$(MANAGE) shell

import_samples: $(SAMPLES)
$(SAMPLES):
	$(MANAGE) import --path $@ --database sample

import_pedigrees: $(PEDIGREES)
$(PEDIGREES):
	$(MANAGE) import --path $@ --database pedigree

import_annotations: $(ANNOTATIONS)
$(ANNOTATIONS):
	$(MANAGE) import --path $@ --database annotation

import_exac: ../tenderloin/exac/ExAC.r0.3.1.sites.vep.biallelic.header.tsv
	$(MANAGE) import --path $< --database exac --release "r0.3.1"

import_hgnc: ../tenderloin/hgnc/hgnc_complete_set.header.txt
	$(MANAGE) import --path $< --database hgnc --release "2018-07-19"

import_hpo: ../tenderloin/hpo/phenotype.header.hpoa
	$(MANAGE) import --path $< --database hpo --release "2018-07-19"

import_omim: ../tenderloin/omim/mim2gene_medgen.header
	$(MANAGE) import --path $< --database omim --release "2018-07-19"

test:
	$(MANAGE) test

import: import_exac import_hgnc import_samples import_annotations import_pedigrees import_hpo import_omim
