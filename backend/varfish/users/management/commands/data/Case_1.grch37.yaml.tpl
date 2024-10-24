# family with only metadata field
family:
  proband:
    id: index
    subject:
      id: index
      sex: MALE
      karyotypicSex: XY
    phenotypicFeatures:
      - type:
          id: "HP:0012469"
          label: "Infantile spasms"
        excluded: false
        modifiers:
          - id: "HP:0031796"
            label: "Recurrent"
    measurements:
      - assay:
          id: NCIT:C158253
          label: Targeted Genome Sequencing
        value:
          ontologyClass:
            id: NCIT:C171177
            label: Sequencing Data File
    files:
      - uri: s3://varfish-server/seqmeta/exon-set/grch37/all-coding-exons-1.0.bed.gz
        individualToFileIdentifiers:
          index: {{ data_case }}_index
        fileAttributes:
          checksum: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
          designation: sequencing_targets
          genomebuild: grch38
          mimetype: text/x-bed+x-bgzip
      # - uri: s3://data-for-import/example/index.bam
      #   individualToFileIdentifiers:
      #     mother: {{ data_case }}_mother
      #   fileAttributes:
      #     checksum: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      #     designation: read_alignments
      #     genomebuild: grch38
      #     mimetype: text/x-bam+x-bgzip
    diseases:
      - term:
          id: OMIM:164400
          label: "SPINOCEREBELLAR ATAXIA 1; SCA1"
        excluded: false
    metaData: &metadata-prototype
      created: "2019-07-21T00:25:54.662Z"
      createdBy: Peter N. Robinson
      resources:
        - id: hp
          name: human phenotype ontology
          url: http://purl.obolibrary.org/obo/hp.owl
          version: "2018-03-08"
          namespacePrefix: HP
          iriPrefix: hp
      phenopacketSchemaVersion: "2.0"
  relatives:
    - id: mother
      subject:
        id: mother
        sex: FEMALE
        karyotypicSex: XX
      phenotypicFeatures:
        - type:
            id: "HP:0012469"
            label: "Infantile spasms"
          excluded: true
      measurements:
        - assay:
            id: NCIT:C158253
            label: Targeted Genome Sequencing
          value:
            ontologyClass:
              id: NCIT:C171177
              label: Sequencing Data File
      files:
        - uri: s3://varfish-server/seqmeta/exon-set/grch37/all-coding-exons-1.0.bed.gz
          individualToFileIdentifiers:
            mother: {{ data_case }}_mother
          fileAttributes:
            checksum: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
            designation: sequencing_targets
            genomebuild: grch38
            mimetype: text/x-bed+x-bgzip
        # - uri: s3://data-for-import/example/mother.bam
        #   individualToFileIdentifiers:
        #     mother: {{ data_case }}_mother
        #   fileAttributes:
        #     checksum: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        #     designation: read_alignments
        #     genomebuild: grch38
        #     mimetype: text/x-bam+x-bgzip
      diseases:
        - term:
            id: OMIM:164400
            label: "SPINOCEREBELLAR ATAXIA 1; SCA1"
          excluded: true
      metaData: *metadata-prototype
    - id: father
      subject:
        id: father
        sex: MALE
        karyotypicSex: XY
      phenotypicFeatures:
        - type:
            id: "HP:0012469"
            label: "Infantile spasms"
          excluded: true
      measurements:
        - assay:
            id: NCIT:C158253
            label: Targeted Genome Sequencing
          value:
            ontologyClass:
              id: NCIT:C171177
              label: Sequencing Data File
      files:
        - uri: s3://varfish-server/seqmeta/exon-set/grch37/all-coding-exons-1.0.bed.gz
          individualToFileIdentifiers:
            father: {{ data_case }}_father
          fileAttributes:
            checksum: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
            designation: sequencing_targets
            genomebuild: grch38
            mimetype: text/x-bed+x-bgzip
        # - uri: s3://data-for-import/example/father.bam
        #   individualToFileIdentifiers:
        #     father: {{ data_case }}_father
        #   fileAttributes:
        #     checksum: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        #     designation: read_alignments
        #     genomebuild: grch38
        #     mimetype: text/x-bam+x-bgzip
      diseases:
        - term:
            id: OMIM:164400
            label: "SPINOCEREBELLAR ATAXIA 1; SCA1"
          excluded: true
      metaData: *metadata-prototype
  pedigree:
    persons:
      - familyId: {{ case_name }}
        individualId: index
        paternalId: father
        maternalId: mother
        sex: MALE
        affectedStatus: AFFECTED
      - familyId: {{ case_name }}
        individualId: father
        paternalId: "0"
        maternalId: "0"
        sex: MALE
        affectedStatus: UNAFFECTED
      - familyId: {{ case_name }}
        individualId: mother
        paternalId: "0"
        maternalId: "0"
        sex: FEMALE
        affectedStatus: UNAFFECTED
  metaData: *metadata-prototype
  files:
    - uri: file://{{ data_path }}/{{ data_case }}.grch37.gatk_hc.vcf.gz
      individualToFileIdentifiers:
        index: {{ data_case }}_index
        father: {{ data_case }}_father
        mother: {{ data_case }}_mother
      fileAttributes:
        checksum: sha256:7104962533dec7a435cdc32785d7bd01caffc87bd68e6edf3c25d43c8136b622
        designation: variant_calls
        variant_type: seqvars
        genomebuild: grch37
        mimetype: text/plain+x-bgzip+x-variant-call-format
