# -*- coding: utf-8 -*-
"""Setup ``variants_smallvariants`` table as partitioned.
"""

from django.db import migrations, models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.conf import settings


operations = [
    migrations.RunSQL(
        r"""SELECT 1""",
        r"""
        DROP MATERIALIZED VIEW IF EXISTS variants_smallvariantsummary;

        CREATE MATERIALIZED VIEW variants_smallvariantsummary
        AS
            SELECT
                row_number() OVER (PARTITION BY true) AS id,
                release,
                chromosome,
                start,
                "end",
                bin,
                reference,
                alternative,
                sum(num_hom_ref) AS count_hom_ref,
                sum(num_het) AS count_het,
                sum(num_hom_alt) AS count_hom_alt,
                sum(num_hemi_ref) AS count_hemi_ref,
                sum(num_hemi_alt) AS count_hemi_alt
            FROM (
                SELECT DISTINCT
                    variants.release,
                    variants.chromosome,
                    variants.start,
                    variants."end",
                    variants.bin,
                    variants.reference,
                    variants.alternative,
                    variants.num_hom_ref,
                    variants.num_het,
                    variants.num_hom_alt,
                    variants.num_hemi_ref,
                    variants.num_hemi_alt,
                    variants.set_id
                FROM variants_smallvariant AS variants
            ) AS variants_per_case
            GROUP BY (release, chromosome, start, "end", bin, reference, alternative)
        WITH DATA;

        CREATE UNIQUE INDEX variants_smallvariantsummary_id ON variants_smallvariantsummary(id);
        CREATE INDEX variants_smallvariantsummary_coord ON variants_smallvariantsummary(
            release, chromosome, start, "end", bin, reference, alternative
        );
        """,
    ),
    migrations.DeleteModel(name="SmallVariant"),
    migrations.CreateModel(
        name="SmallVariant",
        fields=[
            (
                "id",
                models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                ),
            ),
            ("release", models.CharField(max_length=32)),
            ("chromosome", models.CharField(max_length=32)),
            ("chromosome_no", models.IntegerField()),
            ("start", models.IntegerField()),
            ("end", models.IntegerField()),
            ("bin", models.IntegerField()),
            ("reference", models.CharField(max_length=512)),
            ("alternative", models.CharField(max_length=512)),
            ("var_type", models.CharField(max_length=8)),
            ("case_id", models.IntegerField()),
            ("set_id", models.IntegerField()),
            ("genotype", JSONField()),
            ("num_hom_alt", models.IntegerField(default=0)),
            ("num_hom_ref", models.IntegerField(default=0)),
            ("num_het", models.IntegerField(default=0)),
            ("num_hemi_alt", models.IntegerField(default=0)),
            ("num_hemi_ref", models.IntegerField(default=0)),
            ("in_clinvar", models.NullBooleanField()),
            ("exac_frequency", models.FloatField(null=True)),
            ("exac_homozygous", models.IntegerField(null=True)),
            ("exac_heterozygous", models.IntegerField(null=True)),
            ("exac_hemizygous", models.IntegerField(null=True)),
            ("thousand_genomes_frequency", models.FloatField(null=True)),
            ("thousand_genomes_homozygous", models.IntegerField(null=True)),
            ("thousand_genomes_heterozygous", models.IntegerField(null=True)),
            ("thousand_genomes_hemizygous", models.IntegerField(null=True)),
            ("gnomad_exomes_frequency", models.FloatField(null=True)),
            ("gnomad_exomes_homozygous", models.IntegerField(null=True)),
            ("gnomad_exomes_heterozygous", models.IntegerField(null=True)),
            ("gnomad_exomes_hemizygous", models.IntegerField(null=True)),
            ("gnomad_genomes_frequency", models.FloatField(null=True)),
            ("gnomad_genomes_homozygous", models.IntegerField(null=True)),
            ("gnomad_genomes_heterozygous", models.IntegerField(null=True)),
            ("gnomad_genomes_hemizygous", models.IntegerField(null=True)),
            ("refseq_gene_id", models.CharField(max_length=16, null=True)),
            ("refseq_transcript_id", models.CharField(max_length=16, null=True)),
            ("refseq_transcript_coding", models.NullBooleanField()),
            ("refseq_hgvs_c", models.CharField(max_length=512, null=True)),
            ("refseq_hgvs_p", models.CharField(max_length=512, null=True)),
            ("refseq_effect", ArrayField(models.CharField(max_length=64), null=True)),
            ("ensembl_gene_id", models.CharField(max_length=16, null=True)),
            ("ensembl_transcript_id", models.CharField(max_length=16, null=True)),
            ("ensembl_transcript_coding", models.NullBooleanField()),
            ("ensembl_hgvs_c", models.CharField(max_length=512, null=True)),
            ("ensembl_hgvs_p", models.CharField(max_length=512, null=True)),
            ("ensembl_effect", ArrayField(models.CharField(max_length=64, null=True))),
        ],
        options={"db_table": "variants_smallvariant", "managed": settings.IS_TESTING},
    ),
]


if not settings.IS_TESTING:
    sql_partitions = [
        (
            r"""CREATE TABLE variants_smallvariant_%(i)d PARTITION OF variants_smallvariant """
            r"""FOR VALUES WITH (MODULUS %(modulus)d, REMAINDER %(i)d);"""
        )
        % {"i": i, "modulus": settings.VARFISH_PARTITION_MODULUS_SMALLVARIANT}
        for i in range(settings.VARFISH_PARTITION_MODULUS_SMALLVARIANT)
    ]
    operations.append(
        migrations.RunSQL(
            r"""
            CREATE TABLE variants_smallvariant (
                id bigint NOT NULL,
                release character varying(32) NOT NULL,
                chromosome character varying(32) NOT NULL,
                chromosome_no integer NOT NULL,
                start integer NOT NULL,
                "end" integer NOT NULL,
                bin integer NOT NULL,
                reference character varying(512) NOT NULL,
                alternative character varying(512) NOT NULL,
                var_type character varying(8) NOT NULL,
                case_id integer NOT NULL,
                set_id integer NOT NULL,
                genotype jsonb NOT NULL,
                in_clinvar boolean,
                exac_frequency double precision,
                exac_homozygous integer,
                exac_heterozygous integer,
                exac_hemizygous integer,
                thousand_genomes_frequency double precision,
                thousand_genomes_homozygous integer,
                thousand_genomes_heterozygous integer,
                thousand_genomes_hemizygous integer,
                gnomad_exomes_frequency double precision,
                gnomad_exomes_homozygous integer,
                gnomad_exomes_heterozygous integer,
                gnomad_exomes_hemizygous integer,
                gnomad_genomes_frequency double precision,
                gnomad_genomes_homozygous integer,
                gnomad_genomes_heterozygous integer,
                gnomad_genomes_hemizygous integer,
                refseq_gene_id character varying(16),
                refseq_transcript_id character varying(16),
                refseq_transcript_coding boolean,
                refseq_hgvs_c character varying(512),
                refseq_hgvs_p character varying(512),
                refseq_effect character varying(64)[],
                ensembl_gene_id character varying(16),
                ensembl_transcript_id character varying(16),
                ensembl_transcript_coding boolean,
                ensembl_hgvs_c character varying(512),
                ensembl_hgvs_p character varying(512),
                ensembl_effect character varying(64)[] NOT NULL,
                num_hemi_alt integer NOT NULL,
                num_hemi_ref integer NOT NULL,
                num_het integer NOT NULL,
                num_hom_alt integer NOT NULL,
                num_hom_ref integer NOT NULL
            ) PARTITION BY HASH (case_id);

            ALTER TABLE ONLY variants_smallvariant
                ADD CONSTRAINT variants_smallvariant_pkey PRIMARY KEY (id, case_id);

            CREATE INDEX variants_sm_case_id_071d6b_gin ON variants_smallvariant USING gin (case_id, ensembl_effect);
            CREATE INDEX variants_sm_case_id_1f4f31_idx ON variants_smallvariant USING btree (case_id, refseq_gene_id);
            CREATE INDEX variants_sm_case_id_3efbb1_idx ON variants_smallvariant USING btree (case_id, chromosome, bin);
            CREATE INDEX variants_sm_case_id_423a80_idx ON variants_smallvariant USING btree (case_id, in_clinvar);
            CREATE INDEX variants_sm_case_id_5d52f6_idx ON variants_smallvariant USING btree (case_id, ensembl_gene_id);
            CREATE INDEX variants_sm_case_id_6f9d8c_idx ON variants_smallvariant USING btree (case_id);
            CREATE INDEX variants_sm_case_id_a529e8_gin ON variants_smallvariant USING gin (case_id, refseq_effect);

            CREATE SEQUENCE variants_smallvariant_id_seq
                AS integer
                START WITH 1
                INCREMENT BY 1
                NO MINVALUE
                NO MAXVALUE
                CACHE 1;
            ALTER SEQUENCE variants_smallvariant_id_seq OWNED BY variants_smallvariant.id;
            ALTER TABLE ONLY variants_smallvariant ALTER COLUMN id SET DEFAULT nextval('variants_smallvariant_id_seq'::regclass);

            DROP MATERIALIZED VIEW IF EXISTS variants_smallvariantsummary;

            CREATE MATERIALIZED VIEW variants_smallvariantsummary
            AS
                SELECT
                    row_number() OVER (PARTITION BY true) AS id,
                    release,
                    chromosome,
                    chromosome_no,
                    start,
                    "end",
                    bin,
                    reference,
                    alternative,
                    sum(num_hom_ref) AS count_hom_ref,
                    sum(num_het) AS count_het,
                    sum(num_hom_alt) AS count_hom_alt,
                    sum(num_hemi_ref) AS count_hemi_ref,
                    sum(num_hemi_alt) AS count_hemi_alt
                FROM (
                    SELECT DISTINCT
                        variants.release,
                        variants.chromosome,
                        variants.chromosome_no,
                        variants.start,
                        variants."end",
                        variants.bin,
                        variants.reference,
                        variants.alternative,
                        variants.num_hom_ref,
                        variants.num_het,
                        variants.num_hom_alt,
                        variants.num_hemi_ref,
                        variants.num_hemi_alt,
                        variants.case_id,
                        variants.set_id
                    FROM variants_smallvariant AS variants
                ) AS variants_per_case
                GROUP BY (release, chromosome, chromosome_no, start, "end", bin, reference, alternative)
            WITH DATA;

            CREATE UNIQUE INDEX variants_smallvariantsummary_id ON variants_smallvariantsummary(id);
            CREATE INDEX variants_smallvariantsummary_coord ON variants_smallvariantsummary(
                release, chromosome, start, "end", bin, reference, alternative
            );
            """
            + "\n".join(sql_partitions),
            r"""
            DROP TABLE variants_smallvariant CASCADE;
            """,
        )
    )


class Migration(migrations.Migration):

    dependencies = [("variants", "0045_auto_20190628_1233")]

    operations = operations
