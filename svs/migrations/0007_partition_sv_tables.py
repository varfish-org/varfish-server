# -*- coding: utf-8 -*-
"""Setup ``svs`` tables as partitioned.
"""

from django.db import migrations, models
from django.conf import settings
import django.contrib.postgres.fields
import uuid


operations = [
    migrations.DeleteModel("StructuralVariant"),
    migrations.CreateModel(
        name="StructuralVariant",
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
            ("start_ci_left", models.IntegerField()),
            ("start_ci_right", models.IntegerField()),
            ("end_ci_left", models.IntegerField()),
            ("end_ci_right", models.IntegerField()),
            ("case_id", models.IntegerField()),
            ("set_id", models.IntegerField()),
            (
                "sv_uuid",
                models.UUIDField(
                    default=uuid.uuid4, help_text="Structural variant UUID", unique=True
                ),
            ),
            ("caller", models.CharField(max_length=128)),
            (
                "sv_type",
                models.CharField(
                    choices=[
                        ("DEL", "deletion"),
                        ("DUP", "duplication"),
                        ("INS", "insertion"),
                        ("INV", "inversion"),
                        ("BND", "breakend"),
                        ("CNV", "copy number variation"),
                    ],
                    max_length=32,
                ),
            ),
            (
                "sv_sub_type",
                models.CharField(
                    choices=[
                        ("DEL", "deletion"),
                        ("DEL:ME", "mobile element deletion"),
                        ("DEL:ME:SVA", "mobile element deletion (SVA)"),
                        ("DEL:ME:L1", "mobile element deletion (LINE1)"),
                        ("DEL:ME:ALU", "mobile element deletion (ALU)"),
                        ("DUP", "duplication"),
                        ("DUP:TANDEM", "tandem duplication"),
                        ("INV", "inversion"),
                        ("INS", "insertion"),
                        ("INS:ME", "mobile_element insertion"),
                        ("INS:ME:SVA", "mobile element deletion (SVA)"),
                        ("INS:ME:L1", "mobile element deletion (LINE1)"),
                        ("INS:ME:ALU", "mobile element deletion (ALU)"),
                        ("INV", "inversion"),
                        ("BND", "breakend"),
                        ("CNV", "copy number variation"),
                    ],
                    max_length=32,
                ),
            ),
            (
                "info",
                django.contrib.postgres.fields.jsonb.JSONField(
                    default={}, help_text="Further information of the structural variant"
                ),
            ),
            ("genotype", django.contrib.postgres.fields.jsonb.JSONField()),
        ],
        options={"db_table": "svs_structuralvariant", "managed": settings.IS_TESTING},
    ),
    migrations.DeleteModel("StructuralVariantGeneAnnotation"),
    migrations.CreateModel(
        name="StructuralVariantGeneAnnotation",
        fields=[
            (
                "id",
                models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                ),
            ),
            ("case_id", models.IntegerField()),
            ("set_id", models.IntegerField()),
            (
                "sv_uuid",
                models.UUIDField(
                    default=uuid.uuid4, help_text="Structural variant UUID foreign key"
                ),
            ),
            ("refseq_gene_id", models.CharField(max_length=16, null=True)),
            ("refseq_transcript_id", models.CharField(max_length=16, null=True)),
            ("refseq_transcript_coding", models.NullBooleanField()),
            (
                "refseq_effect",
                django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=64), null=True, size=None
                ),
            ),
            ("ensembl_gene_id", models.CharField(max_length=16, null=True)),
            ("ensembl_transcript_id", models.CharField(max_length=16, null=True)),
            ("ensembl_transcript_coding", models.NullBooleanField()),
            (
                "ensembl_effect",
                django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=64, null=True), size=None
                ),
            ),
        ],
        options={"db_table": "svs_structuralvariantgeneannotation", "managed": settings.IS_TESTING},
    ),
]

if not settings.IS_TESTING:
    sql_partitions = [
        (
            r"""CREATE TABLE svs_structuralvariant%(i)d PARTITION OF svs_structuralvariant """
            r"""FOR VALUES WITH (MODULUS %(modulus)d, REMAINDER %(i)d);"""
            r"""CREATE TABLE svs_structuralvariantgeneannotation%(i)d PARTITION OF """
            r"""svs_structuralvariantgeneannotation FOR VALUES WITH (MODULUS %(modulus)d, REMAINDER %(i)d);"""
        )
        % {"i": i, "modulus": settings.VARFISH_PARTITION_MODULUS_SVS}
        for i in range(settings.VARFISH_PARTITION_MODULUS_SVS)
    ]
    operations.append(
        migrations.RunSQL(
            r"""
            DROP TABLE IF EXISTS svs_structuralvariant CASCADE;
            
            CREATE TABLE svs_structuralvariant (
                id integer NOT NULL,
                release character varying(32) NOT NULL,
                chromosome character varying(32) NOT NULL,
                start integer NOT NULL,
                "end" integer NOT NULL,
                bin integer NOT NULL,
                start_ci_left integer NOT NULL,
                start_ci_right integer NOT NULL,
                end_ci_left integer NOT NULL,
                end_ci_right integer NOT NULL,
                case_id integer NOT NULL,
                set_id integer NOT NULL,
                sv_uuid uuid NOT NULL,
                caller character varying(128) NOT NULL,
                sv_type character varying(32) NOT NULL,
                sv_sub_type character varying(32) NOT NULL,
                info jsonb NOT NULL,
                genotype jsonb NOT NULL,
                chromosome_no integer NOT NULL
            ) PARTITION BY HASH (case_id);

            ALTER TABLE ONLY svs_structuralvariant
                ADD CONSTRAINT svs_structuralvariant_pkey PRIMARY KEY (id, case_id);

            CREATE SEQUENCE svs_structuralvariant_id_seq
                AS integer
                START WITH 1
                INCREMENT BY 1
                NO MINVALUE
                NO MAXVALUE
                CACHE 1;

            ALTER TABLE ONLY svs_structuralvariant
                ALTER COLUMN id SET DEFAULT nextval('svs_structuralvariant_id_seq'::regclass);
            ALTER TABLE ONLY svs_structuralvariant
                ADD CONSTRAINT svs_structuralvariant_sv_uuid_key UNIQUE (sv_uuid, case_id);
            CREATE INDEX svs_structu_case_id_988c93_idx ON svs_structuralvariant
                USING btree (case_id);
            CREATE INDEX svs_structu_case_id_aa8632_idx ON svs_structuralvariant
                USING btree (case_id, release, chromosome, bin, sv_type, sv_sub_type);
            CREATE INDEX svs_structu_case_id_cd8553_idx ON svs_structuralvariant
                USING btree (case_id, release, chromosome, bin);
            CREATE INDEX svs_structu_set_id_951ec1_idx ON svs_structuralvariant
                USING btree (set_id);
            
            DROP TABLE IF EXISTS svs_structuralvariantgeneannotation CASCADE;

            CREATE TABLE svs_structuralvariantgeneannotation (
                id integer NOT NULL,
                sv_uuid uuid NOT NULL,
                refseq_gene_id character varying(16),
                refseq_transcript_id character varying(32),
                refseq_transcript_coding boolean,
                refseq_effect character varying(64)[],
                ensembl_gene_id character varying(32),
                ensembl_transcript_id character varying(32),
                ensembl_transcript_coding boolean,
                ensembl_effect character varying(64)[] NOT NULL,
                case_id integer NOT NULL,
                set_id integer NOT NULL
            ) PARTITION BY HASH (case_id);

            ALTER TABLE ONLY svs_structuralvariantgeneannotation
                ADD CONSTRAINT svs_structuralvariantgeneannotation_pkey PRIMARY KEY (id, case_id);

            CREATE SEQUENCE svs_structuralvariantgeneannotation_id_seq
                AS integer
                START WITH 1
                INCREMENT BY 1
                NO MINVALUE
                NO MAXVALUE
                CACHE 1;

            ALTER TABLE ONLY svs_structuralvariantgeneannotation
                ALTER COLUMN id SET DEFAULT nextval('svs_structuralvariantgeneannotation_id_seq'::regclass);
            CREATE INDEX svs_structu_set_id_42f2ba_idx ON svs_structuralvariantgeneannotation
                USING btree (set_id);
            CREATE INDEX svs_structu_sv_uuid_09c0c4_idx ON svs_structuralvariantgeneannotation
                USING btree (sv_uuid);

            """
            + "\n".join(sql_partitions),
            r"""
            DROP TABLE IF EXISTS svs_structuralvariant CASCADE;
            DROP SEQUENCE IF EXISTS svs_structuralvariant_id_seq CASCADE;
            DROP TABLE IF EXISTS svs_structuralvariantgeneannotation CASCADE;
            DROP SEQUENCE IF EXISTS svs_structuralvariantgeneannotation_id_seq CASCADE;
            """,
        )
    )


class Migration(migrations.Migration):

    dependencies = [("svs", "0006_auto_20190703_1709")]

    operations = operations
