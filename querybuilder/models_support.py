class QueryBuilder:
    def __init__(self):
        self.count = 0

    def _next_int(self):
        ret = self.count
        self.count += 1
        return ret

    def _next_name(self):
        return "name{}".format(self._next_int())

    def _het_query_part(self, population=None):
        if not population:
            return "ac - 2 * hom - COALESCE(hemi, 0) AS het"

        return "ac_{p} - 2 * hom_{p} - COALESCE(hemi_{p}, 0) AS het_{p}".format(p=population)

    def _frequency_selector(self, table, fields, populations):
        selector = list()

        for typ in fields:
            if typ == "het" and not table == "thousandgenomes":
                selector.append(self._het_query_part())
            else:
                selector.append(typ)
            for population in populations:
                if table == "thousandgenomes":
                    if typ == "af":
                        selector.append("{}_{}".format(typ, population))
                    continue

                if typ == "het":
                    selector.append(self._het_query_part(population))
                else:
                    selector.append("{}_{}".format(typ, population))

        return ", ".join(selector)

    def _build_frequency_query(self, kwargs, table, fields, populations):
        name_rel = self._next_name()
        name_chr = self._next_name()
        name_pos = self._next_name()
        name_ref = self._next_name()
        name_alt = self._next_name()
        selector = self._frequency_selector(table, fields, populations)

        return (
            r"""
            SELECT id, {}
            FROM frequencies_{}
            WHERE ((release = %({})s) AND
                (chromosome = %({})s) AND
                (position = %({})s) AND
                (reference = %({})s) AND
                (alternative = %({})s))
            """.format(
                selector, table, name_rel, name_chr, name_pos, name_ref, name_alt
            ),
            {
                name_rel: kwargs["release"],
                name_chr: kwargs["chromosome"],
                name_pos: kwargs["position"],
                name_ref: kwargs["reference"],
                name_alt: kwargs["alternative"],
            },
        )

    def build_gnomadgenomes_query(self, kwargs):
        return self._build_frequency_query(
            kwargs,
            "gnomadgenomes",
            fields=("af", "an", "ac", "hom", "hemi", "het"),
            populations=("afr", "amr", "asj", "eas", "fin", "nfe", "oth"),
        )

    def build_gnomadexomes_query(self, kwargs):
        return self._build_frequency_query(
            kwargs,
            "gnomadexomes",
            fields=("af", "an", "ac", "hom", "hemi", "het"),
            populations=("afr", "amr", "asj", "eas", "fin", "nfe", "oth", "sas"),
        )

    def build_exac_query(self, kwargs):
        return self._build_frequency_query(
            kwargs,
            "exac",
            fields=("af", "an", "ac", "hom", "hemi", "het"),
            populations=("afr", "amr", "eas", "fin", "nfe", "oth", "sas"),
        )

    def build_thousandgenomes_query(self, kwargs):
        return self._build_frequency_query(
            kwargs,
            "thousandgenomes",
            fields=("af", "an", "ac", "hom", "het"),
            populations=("afr", "amr", "eas", "eur", "sas"),
        )

    def build_knowngeneaa_query(self, kwargs):
        name_chr = self._next_name()
        name_start = self._next_name()
        name_end = self._next_name()

        return (
            r"""
            SELECT DISTINCT(chromosome, start, "end"), 1 AS id, chromosome, start, "end", alignment
            FROM conservation_knowngeneaa
            WHERE (
                (chromosome = %({})s) AND
                (start <= %({})s) AND
                ("end" >= %({})s)
            )
            """.format(
                name_chr, name_end, name_start
            ),
            {
                name_chr: kwargs["chromosome"],
                name_start: int(kwargs["position"]),
                name_end: int(kwargs["position"]) + len(kwargs["reference"]) - 1,
            },
        )

    def build_comphet_query(self, kwargs):
        query, args = self.build_comphet_sub_query(kwargs)

        if not kwargs["database_select"] in ("refseq", "ensembl"):
            return "FALSE"

        hgnc = ""
        database = ""

        if kwargs["database_select"] == "refseq":
            database = "refseq"
            hgnc = "ON (refseq_gene_id = h.entrez_id)"
        elif kwargs["database_select"] == "ensembl":
            database = "ensembl"
            hgnc = "USING (ensembl_gene_id)"

        return (
            r"""
            SELECT
                1 AS id,
                release, chromosome, position, reference, alternative,
                exac_frequency,
                gnomad_exomes_frequency,
                gnomad_genomes_frequency,
                thousand_genomes_frequency,
                exac_homozygous,
                gnomad_exomes_homozygous,
                gnomad_genomes_homozygous,
                thousand_genomes_homozygous,
                genotype,
                pedigree,
                index,
                case_id,
                in_clinvar,
                h.symbol,
                d.rsid,
                {database}_hgvs_p,
                {database}_hgvs_c,
                {database}_transcript_coding,
                {database}_effect,
                {database}_gene_id AS gene_id
            FROM ({query}) sv
            LEFT OUTER JOIN dbsnp_dbsnp d USING (release, chromosome, position, reference, alternative)
            LEFT OUTER JOIN geneinfo_hgnc h {hgnc}
            WHERE
                (p1_c > 0) AND
                (p2_c > 0);
            """.format(
                database=database, hgnc=hgnc, query=query
            ),
            args,
        )

    def build_comphet_query_part(self, gt_father, gt_mother, kwargs):
        conditions = [
            self.build_vartype_term(kwargs),
            self.build_frequency_term(kwargs),
            self.build_homozygous_term(kwargs),
            self.build_heterozygous_term(kwargs),
            self.build_case_term(kwargs),
            self.build_effects_term(kwargs),
            self.build_gene_blacklist_term(kwargs),
            self.build_comphet_gt_query(kwargs),
        ]

        condition_list = list()
        args_merged = dict()
        for condition, args in conditions:
            condition_list.append(condition)
            args_merged = {**args_merged, **args}

        conditions_joined = " AND ".join("({})".format(condition) for condition in condition_list)

        roles = dict()
        for member in kwargs["pedigree"]:
            roles[member["role"]] = member["patient"]

        if not kwargs["database_select"] in ("refseq", "ensembl"):
            return ("(FALSE)", {})

        name_index = self._next_name()
        name_mother = self._next_name()
        name_father = self._next_name()

        return (
            r"""
            SELECT *, {as_p1} AS p1, {as_p2} AS p2
            FROM variants_smallvariant AS sv
            LEFT OUTER JOIN variants_case c ON (sv.case_id = c.id)
            WHERE (
                (genotype->%({index})s->>'gt' = '0/1') AND
                (genotype->%({mother})s->>'gt' = '{gt_mother}') AND
                (genotype->%({father})s->>'gt' = '{gt_father}') AND
                ({database}_gene_id IS NOT NULL) AND
                ({conditions})
            )
            """.format(
                mother=name_mother,
                father=name_father,
                index=name_index,
                database=kwargs["database_select"],
                conditions=conditions_joined,
                gt_father=gt_father,
                gt_mother=gt_mother,
                as_p1=0 if gt_father == "0/0" else 1,
                as_p2=0 if gt_mother == "0/0" else 1,
            ),
            {
                **args_merged,
                name_index: roles["index"],
                name_mother: roles["mother"],
                name_father: roles["father"],
            },
        )

    def build_comphet_gt_query(self, kwargs):
        return self._build_gt_inner(self.build_genotype_quality_term, kwargs)

    def build_comphet_sub_query(self, kwargs):
        query_p1, args_p1 = self.build_comphet_query_part("0/1", "0/0", kwargs)
        query_p2, args_p2 = self.build_comphet_query_part("0/0", "0/1", kwargs)

        if not kwargs["database_select"] in ("refseq", "ensembl"):
            return "FALSE"

        return (
            r"""
            SELECT *,
                SUM(p1) OVER (PARTITION BY {database}_gene_id) AS p1_c,
                SUM(p2) OVER (PARTITION BY {database}_gene_id) AS p2_c
            FROM (
                ({query_p1})
                UNION
                ({query_p2})
            ) AS a
            """.format(
                database=kwargs["database_select"], query_p1=query_p1, query_p2=query_p2
            ),
            {**args_p1, **args_p2},
        )

    def build_base_query(self, kwargs):
        if not kwargs["database_select"] in ("refseq", "ensembl"):
            return "FALSE"

        hgnc = ""
        database = ""

        if kwargs["database_select"] == "refseq":
            database = "refseq"
            hgnc = "ON (sv.refseq_gene_id = h.entrez_id)"
        elif kwargs["database_select"] == "ensembl":
            database = "ensembl"
            hgnc = "USING (ensembl_gene_id)"

        return r"""
            SELECT
                sv.id,
                sv.release, sv.chromosome, sv.position, sv.reference, sv.alternative,
                sv.exac_frequency,
                sv.gnomad_exomes_frequency,
                sv.gnomad_genomes_frequency,
                sv.thousand_genomes_frequency,
                sv.exac_homozygous,
                sv.gnomad_exomes_homozygous,
                sv.gnomad_genomes_homozygous,
                sv.thousand_genomes_homozygous,
                sv.genotype,
                sv.case_id,
                sv.in_clinvar,
                h.symbol,
                c.pedigree,
                c.index,
                d.rsid,
                sv.{database}_hgvs_p,
                sv.{database}_hgvs_c,
                sv.{database}_transcript_coding,
                sv.{database}_effect,
                sv.{database}_gene_id AS gene_id
            FROM variants_smallvariant sv
            LEFT OUTER JOIN variants_case c ON (sv.case_id = c.id)
            LEFT OUTER JOIN dbsnp_dbsnp d USING (release, chromosome, position, reference, alternative)
            LEFT OUTER JOIN geneinfo_hgnc h {hgnc}
            """.format(
            database=database, hgnc=hgnc
        )

    def build_vartype_term(self, kwargs):
        values = list()

        if kwargs["var_type_snv"]:
            values.append("'snv'")
        if kwargs["var_type_mnv"]:
            values.append("'mnv'")
        if kwargs["var_type_indel"]:
            values.append("'indel'")

        return ("(sv.var_type in ({}))".format(",".join(values)), {})

    def build_frequency_term(self, kwargs):
        name_gnomad_exomes = self._next_name()
        name_gnomad_genomes = self._next_name()
        name_exac = self._next_name()
        name_thousand_genomes = self._next_name()
        query_string = " AND ".join(
            [
                "(sv.exac_frequency <= %({exac})s)"
                if (kwargs["exac_enabled"] and kwargs["exac_frequency"])
                else "TRUE",
                "(sv.gnomad_exomes_frequency <= %({gnomad_exomes})s)"
                if (kwargs["gnomad_exomes_enabled"] and kwargs["gnomad_exomes_frequency"])
                else "TRUE",
                "(sv.gnomad_genomes_frequency <= %({gnomad_genomes})s)"
                if (kwargs["gnomad_genomes_enabled"] and kwargs["gnomad_genomes_frequency"])
                else "TRUE",
                "(sv.thousand_genomes_frequency <= %({thousand_genomes})s)"
                if (kwargs["thousand_genomes_enabled"] and kwargs["thousand_genomes_frequency"])
                else "TRUE",
            ]
        )

        return (
            query_string.format(
                gnomad_exomes=name_gnomad_exomes,
                gnomad_genomes=name_gnomad_genomes,
                exac=name_exac,
                thousand_genomes=name_thousand_genomes,
            ),
            {
                name_gnomad_exomes: kwargs["gnomad_exomes_frequency"],
                name_gnomad_genomes: kwargs["gnomad_genomes_frequency"],
                name_exac: kwargs["exac_frequency"],
                name_thousand_genomes: kwargs["thousand_genomes_frequency"],
            },
        )

    def build_homozygous_term(self, kwargs):
        name_exac = self._next_name()
        name_gnomad_genomes = self._next_name()
        name_gnomad_exomes = self._next_name()
        name_thousand_genomes = self._next_name()
        query_string = " AND ".join(
            [
                "(sv.exac_homozygous <= %({exac})s)"
                if (kwargs["exac_enabled"] and not kwargs["exac_homozygous"] is None)
                else "TRUE",
                "(sv.gnomad_genomes_homozygous <= %({gnomad_genomes})s)"
                if (
                    kwargs["gnomad_genomes_enabled"]
                    and not kwargs["gnomad_genomes_homozygous"] is None
                )
                else "TRUE",
                "(sv.gnomad_exomes_homozygous <= %({gnomad_exomes})s)"
                if (
                    kwargs["gnomad_exomes_enabled"]
                    and not kwargs["gnomad_exomes_homozygous"] is None
                )
                else "TRUE",
                "(sv.thousand_genomes_homozygous <= %({thousand_genomes})s)"
                if (
                    kwargs["thousand_genomes_enabled"]
                    and not kwargs["thousand_genomes_homozygous"] is None
                )
                else "TRUE",
            ]
        )

        return (
            query_string.format(
                exac=name_exac,
                gnomad_genomes=name_gnomad_genomes,
                gnomad_exomes=name_gnomad_exomes,
                thousand_genomes=name_thousand_genomes,
            ),
            {
                name_exac: kwargs["exac_homozygous"],
                name_gnomad_genomes: kwargs["gnomad_genomes_homozygous"],
                name_gnomad_exomes: kwargs["gnomad_exomes_homozygous"],
                name_thousand_genomes: kwargs["thousand_genomes_homozygous"],
            },
        )

    def build_heterozygous_term(self, kwargs):
        name_exac = self._next_name()
        name_gnomad_genomes = self._next_name()
        name_gnomad_exomes = self._next_name()
        name_thousand_genomes = self._next_name()
        query_string = " AND ".join(
            [
                "(sv.exac_heterozygous <= %({exac})s)"
                if (kwargs["exac_enabled"] and not kwargs["exac_heterozygous"] is None)
                else "TRUE",
                "(sv.gnomad_genomes_heterozygous <= %({gnomad_genomes})s)"
                if (
                    kwargs["gnomad_genomes_enabled"]
                    and not kwargs["gnomad_genomes_heterozygous"] is None
                )
                else "TRUE",
                "(sv.gnomad_exomes_heterozygous <= %({gnomad_exomes})s)"
                if (
                    kwargs["gnomad_exomes_enabled"]
                    and not kwargs["gnomad_exomes_heterozygous"] is None
                )
                else "TRUE",
                "(sv.thousand_genomes_heterozygous <= %({thousand_genomes})s)"
                if (
                    kwargs["thousand_genomes_enabled"]
                    and not kwargs["thousand_genomes_heterozygous"] is None
                )
                else "TRUE",
            ]
        )

        return (
            query_string.format(
                exac=name_exac,
                gnomad_genomes=name_gnomad_genomes,
                gnomad_exomes=name_gnomad_exomes,
                thousand_genomes=name_thousand_genomes,
            ),
            {
                name_exac: kwargs["exac_heterozygous"],
                name_gnomad_genomes: kwargs["gnomad_genomes_heterozygous"],
                name_gnomad_exomes: kwargs["gnomad_exomes_heterozygous"],
                name_thousand_genomes: kwargs["thousand_genomes_heterozygous"],
            },
        )

    def build_case_term(self, kwargs):
        name = self._next_name()
        return ("c.sodar_uuid = %({})s".format(name), {name: kwargs["case"]})

    def build_effects_term(self, kwargs):
        if not kwargs["database_select"] in ("refseq", "ensembl"):
            return "FALSE"

        if kwargs["database_select"] == "ensembl":
            database = "ensembl"
        elif kwargs["database_select"] == "refseq":
            database = "refseq"

        args = {self._next_name(): effect for effect in kwargs["effects"]}
        effect_string = ",".join("%({})s".format(name) for name in args)
        return ("(sv.{}_effect && ARRAY[{}]::VARCHAR[])".format(database, effect_string), args)

    def build_genotype_term_list(self, kwargs):
        return self._build_gt_inner(self.build_genotype_term, kwargs)

    def _build_gt_inner(self, build_func, kwargs):
        query_list = list()
        args_merged = dict()
        for member in kwargs["genotype"]:
            query, args = build_func(member)
            query_list.append("({})".format(query))
            args_merged = {**args_merged, **args}
        return (" AND ".join(query_list), args_merged)

    def build_genotype_term(self, kwargs):
        quality_term, quality_args = self.build_genotype_quality_term(kwargs)
        gt_term, gt_args = self.build_genotype_gt_term(kwargs)

        if kwargs["fail"] == "drop-variant":
            tmpl = "({quality})"
            tmpl += " AND ({gt})" if kwargs["gt"] else ""
        elif kwargs["fail"] == "no-call":
            tmpl = "(NOT ({quality}))"
            tmpl += " OR ({gt})" if kwargs["gt"] else ""
        else:
            tmpl = "({gt})" if kwargs["gt"] else "TRUE"
        tmpl = "({})".format(tmpl)

        return (tmpl.format(quality=quality_term, gt=gt_term), {**gt_args, **quality_args})

    def build_gene_blacklist_term(self, kwargs):
        args = {}
        if kwargs["gene_blacklist"]:
            vals = []
            for gene in kwargs["gene_blacklist"]:
                name = self._next_name()
                vals.append("%({})s".format(name))
                args[name] = gene
            qry = "(NOT (ARRAY[h.symbol]::VARCHAR[] && ARRAY[{}]::VARCHAR[]))".format(
                ", ".join(vals)
            )
        else:
            qry = "(TRUE)"
        return (qry, args)

    def build_genotype_quality_term(self, kwargs):
        ad_term, ad_args = self.build_genotype_ad_term(kwargs)
        dp_term, dp_args = self.build_genotype_dp_term(kwargs)
        gq_term, gq_args = self.build_genotype_gq_term(kwargs)
        ab_term, ab_args = self.build_genotype_ab_term(kwargs)

        return (
            " AND ".join("({})".format(x) for x in [ad_term, dp_term, gq_term, ab_term]),
            {**ad_args, **dp_args, **gq_args, **ab_args},
        )

    def build_genotype_ad_term(self, kwargs):
        name1 = self._next_name()
        name2 = self._next_name()

        return (
            r"""
                (
                    ((genotype->%({member})s->>'gt') = '0/0')
                    OR
                    ((genotype->%({member})s->>'ad')::int >= %({ad})s)
                )
            """.format(
                member=name1, ad=name2
            ),
            {name1: kwargs["member"], name2: kwargs["ad"]},
        )

    def build_genotype_dp_term(self, kwargs):
        name1 = self._next_name()
        name2 = self._next_name()
        return (
            "(genotype->%({member})s->>'dp')::int >= %({dp})s".format(member=name1, dp=name2),
            {name1: kwargs["member"], name2: kwargs["dp"]},
        )

    def build_genotype_gq_term(self, kwargs):
        name1 = self._next_name()
        name2 = self._next_name()
        return (
            "(genotype->%({member})s->>'gq')::int >= %({gq})s".format(member=name1, gq=name2),
            {name1: kwargs["member"], name2: kwargs["gq"]},
        )

    def build_genotype_ab_term(self, kwargs):
        name1 = self._next_name()
        name2 = self._next_name()
        return (
            r"""
            ((genotype->%({member})s->>'dp')::int != 0)
            AND
            (
                (((genotype->%({member})s->>'gt') != '0/1') AND ((genotype->%({member})s->>'gt') != '1/0'))
                OR
                (%({ab})s <= ((genotype->%({member})s->>'ad')::float / (genotype->%({member})s->>'dp')::float))
            )
            AND
            (
                (((genotype->%({member})s->>'gt') != '0/1') AND ((genotype->%({member})s->>'gt') != '1/0'))
                OR
                (((genotype->%({member})s->>'ad')::float / (genotype->%({member})s->>'dp')::float) <= (1 - %({ab})s))
            )
            """.format(
                member=name1, ab=name2
            ),
            {name1: kwargs["member"], name2: kwargs["ab"]},
        )

    def build_genotype_gt_term(self, kwargs):
        if not kwargs["gt"]:
            return ("TRUE", {})

        args = {self._next_name(): gt for gt in kwargs["gt"]}
        name_member = self._next_name()
        term = " OR ".join(
            "(genotype->%({member})s->>'gt' = %({gt})s)".format(member=name_member, gt=gt)
            for gt in args
        )
        args[name_member] = kwargs["member"]

        return (term, args)

    def build_top_level_query(self, base, conditions):
        condition_list = list()
        args_merged = dict()
        for condition, args in conditions:
            condition_list.append(condition)
            args_merged = {**args_merged, **args}

        conditions_joined = " AND ".join("({})".format(condition) for condition in condition_list)

        return (
            "{base} WHERE {condition} ORDER BY chromosome, position".format(
                base=base, condition=conditions_joined
            ),
            args_merged,
        )
