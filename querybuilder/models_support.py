from variants.models import SmallVariant
from variants.forms import FILTER_FORM_TRANSLATE_EFFECTS, FILTER_FORM_TRANSLATE_INHERITANCE


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

    def build_comphet_query(self, kwargs, include_conservation=False):
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

        result_tpl = r"""
            SELECT
                %(conservation_distinct)s
                1 AS id,
                sv_outer.release,
                sv_outer.chromosome,
                sv_outer.position,
                sv_outer.reference,
                sv_outer.alternative,
                sv_outer.exac_frequency,
                sv_outer.gnomad_exomes_frequency,
                sv_outer.gnomad_genomes_frequency,
                sv_outer.thousand_genomes_frequency,
                sv_outer.exac_homozygous,
                sv_outer.gnomad_exomes_homozygous,
                sv_outer.gnomad_genomes_homozygous,
                sv_outer.thousand_genomes_homozygous,
                sv_outer.genotype,
                sv_outer.pedigree,
                sv_outer.index,
                sv_outer.case_id,
                sv_outer.in_clinvar,
                h.symbol,
                d.rsid,
                sv_outer.{database}_hgvs_p,
                sv_outer.{database}_hgvs_c,
                sv_outer.{database}_transcript_coding,
                sv_outer.{database}_effect,
                sv_outer.{database}_gene_id AS gene_id
                %(conservation_alignment)s
            FROM ({query}) sv_outer
            LEFT OUTER JOIN dbsnp_dbsnp d USING (release, chromosome, position, reference, alternative)
            LEFT OUTER JOIN geneinfo_hgnc h {hgnc}
            %(conservation_left_join)s
            WHERE
                (p1_c > 0) AND
                (p2_c > 0)
            %(conservation_group_by)s;
            """
        return (
            (result_tpl % self._build_feature_args(include_conservation=include_conservation, sv_name='sv_outer', group_by_sv_id=False)).format(
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

    def build_base_query(self, kwargs, include_conservation=False):
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

        result_tpl = r"""
            SELECT
                %(conservation_distinct)s
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
                %(conservation_alignment)s
            FROM variants_smallvariant sv
            LEFT OUTER JOIN variants_case c ON (sv.case_id = c.id)
            LEFT OUTER JOIN dbsnp_dbsnp d USING (release, chromosome, position, reference, alternative)
            LEFT OUTER JOIN geneinfo_hgnc h {hgnc}
            %(conservation_left_join)s
            WHERE %%(where)s
            %(conservation_group_by)s
            ORDER BY %%(order_by)s
            """
        return (result_tpl % self._build_feature_args(include_conservation)).format(
            database=database, hgnc=hgnc
        )

    def _build_feature_args(self, include_conservation, sv_name="sv", group_by_sv_id=True):
        if include_conservation:
            return {
                'conservation_distinct': r"""
                    DISTINCT(
                        %(sv_name)s.release,
                        %(sv_name)s.chromosome,
                        %(sv_name)s.position,
                        %(sv_name)s.reference,
                        %(sv_name)s.alternative
                    ),
                """ % {'sv_name': sv_name},
                'conservation_alignment': r"""
                , string_agg(kgaa.alignment, ' / ') as known_gene_aa
                """,
                'conservation_left_join': r"""
                LEFT OUTER JOIN conservation_knowngeneaa AS kgaa
                    ON (
                        %(sv_name)s.chromosome = kgaa.chromosome AND
                        (%(sv_name)s.position - 1 + LENGTH(%(sv_name)s.reference)) >= kgaa.start AND
                        (%(sv_name)s.position - 1) < kgaa.end AND
                        -- This is hacky, will not work for versions >9
                        LEFT(h.ucsc_id, -2) = LEFT(kgaa.transcript_id, -2)
                    )
                """ % {'sv_name': sv_name},
                'conservation_group_by': r"""
                GROUP BY
                    %(sv_id)s
                    %(sv_name)s.release,
                    %(sv_name)s.chromosome,
                    %(sv_name)s.position,
                    %(sv_name)s.reference,
                    %(sv_name)s.alternative,
                    %(sv_name)s.exac_frequency,
                    %(sv_name)s.gnomad_exomes_frequency,
                    %(sv_name)s.gnomad_genomes_frequency,
                    %(sv_name)s.thousand_genomes_frequency,
                    %(sv_name)s.exac_homozygous,
                    %(sv_name)s.gnomad_exomes_homozygous,
                    %(sv_name)s.gnomad_genomes_homozygous,
                    %(sv_name)s.thousand_genomes_homozygous,
                    %(sv_name)s.genotype,
                    %(sv_name)s.case_id,
                    %(sv_name)s.in_clinvar,
                    symbol,
                    pedigree,
                    index,
                    rsid,
                    %(sv_name)s.{database}_hgvs_p,
                    %(sv_name)s.{database}_hgvs_c,
                    %(sv_name)s.{database}_transcript_coding,
                    %(sv_name)s.{database}_effect,
                    %(sv_name)s.{database}_gene_id
                """ % {
                    'sv_id': '%s.id,' % sv_name if group_by_sv_id else '',
                    'sv_name': sv_name,
                },
            }
        else:
            return {
                'conservation_distinct': '',
                'conservation_alignment': '',
                'conservation_left_join': '',
                'conservation_group_by': '',
            }

    def build_vartype_term(self, kwargs):
        values = list()

        if kwargs["var_type_snv"]:
            values.append("'snv'")
        if kwargs["var_type_mnv"]:
            values.append("'mnv'")
        if kwargs["var_type_indel"]:
            values.append("'indel'")

        if not values:
            values = ["''"]

        return ("(sv.var_type in ({}))".format(",".join(values)), {})

    def build_frequency_term(self, kwargs):
        name_gnomad_exomes = self._next_name()
        name_gnomad_genomes = self._next_name()
        name_exac = self._next_name()
        name_thousand_genomes = self._next_name()
        query_string = " AND ".join(
            [
                "(sv.exac_frequency <= %({exac})s)"
                if (kwargs["exac_enabled"] and not kwargs["exac_frequency"] is None)
                else "TRUE",
                "(sv.gnomad_exomes_frequency <= %({gnomad_exomes})s)"
                if (kwargs["gnomad_exomes_enabled"] and not kwargs["gnomad_exomes_frequency"] is None)
                else "TRUE",
                "(sv.gnomad_genomes_frequency <= %({gnomad_genomes})s)"
                if (kwargs["gnomad_genomes_enabled"] and not kwargs["gnomad_genomes_frequency"] is None)
                else "TRUE",
                "(sv.thousand_genomes_frequency <= %({thousand_genomes})s)"
                if (kwargs["thousand_genomes_enabled"] and not kwargs["thousand_genomes_frequency"] is None)
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
            base % {'where': conditions_joined, 'order_by': 'chromosome, position'},
            args_merged,
        )


class FilterQueryRunner:
    """Wrapper for ``QueryBuilder`` for using ``QueryBuilder`` from form ``kwargs``."""

    def __init__(self, case, cleaned_data, include_conservation=False):
        self.case = case
        self.cleaned_data = cleaned_data
        self.pedigree = list(self.__class__.build_pedigree(self.case))
        #: Whether or not to include the ``knownGeneAA`` conservation information.
        self.include_conservation = include_conservation

    @staticmethod
    def build_pedigree(case):
        index = case.index
        father = ""
        mother = ""
        for member in case.pedigree:
            if member["patient"] == index:
                father = member["father"]
                mother = member["mother"]

        for member in case.pedigree:
            name = member["patient"]
            if name == father:
                role = "father"
            elif name == index:
                role = "index"
            elif name == mother:
                role = "mother"
            else:
                role = "tbd"
            yield {
                    "patient": name,
                    "father": member["father"],
                    "mother": member["mother"],
                    "gender": member["sex"] == 2,
                    "affected": member["affected"] == 2,
                    "role": role,
                    "fields": {
                        "gt": "%s_gt" % name,
                        "dp": "%s_dp" % name,
                        "ab": "%s_ab" % name,
                        "gq": "%s_gq" % name,
                        "ad": "%s_ad" % name,
                        "fail": "%s_fail" % name,
                        "export": "%s_export" % name,
                    },
                }

    def _collect_select_effects(self):
        """Yield the selected effects."""
        for field_name, effect in FILTER_FORM_TRANSLATE_EFFECTS.items():
            if self.cleaned_data[field_name]:
                yield effect

    def _build_query_kwargs(self):
        """Build the ``kwargs`` variable for ``form_valid`` and friends."""
        selected_effects = self._collect_select_effects()
        pedigree = self.pedigree
        kwargs = {
            "case": self.case.sodar_uuid,
            "exac_frequency": float(self.cleaned_data["exac_frequency"])
            if self.cleaned_data["exac_frequency"]
            else None,
            "exac_homozygous": int(self.cleaned_data["exac_homozygous"])
            if self.cleaned_data["exac_homozygous"]
            else None,
            "exac_heterozygous": int(self.cleaned_data["exac_heterozygous"])
            if self.cleaned_data["exac_heterozygous"]
            else None,
            "gnomad_genomes_frequency": float(self.cleaned_data["gnomad_genomes_frequency"])
            if self.cleaned_data["gnomad_genomes_frequency"]
            else None,
            "gnomad_genomes_homozygous": int(self.cleaned_data["gnomad_genomes_homozygous"])
            if self.cleaned_data["gnomad_genomes_homozygous"]
            else None,
            "gnomad_genomes_heterozygous": int(self.cleaned_data["gnomad_genomes_heterozygous"])
            if self.cleaned_data["gnomad_genomes_heterozygous"]
            else None,
            "gnomad_exomes_frequency": float(self.cleaned_data["gnomad_exomes_frequency"])
            if self.cleaned_data["gnomad_exomes_frequency"]
            else None,
            "gnomad_exomes_homozygous": int(self.cleaned_data["gnomad_exomes_homozygous"])
            if self.cleaned_data["gnomad_exomes_homozygous"]
            else None,
            "gnomad_exomes_heterozygous": int(self.cleaned_data["gnomad_exomes_heterozygous"])
            if self.cleaned_data["gnomad_exomes_heterozygous"]
            else None,
            "thousand_genomes_frequency": float(self.cleaned_data["thousand_genomes_frequency"])
            if self.cleaned_data["thousand_genomes_frequency"]
            else None,
            "thousand_genomes_homozygous": int(self.cleaned_data["thousand_genomes_homozygous"])
            if self.cleaned_data["thousand_genomes_homozygous"]
            else None,
            "thousand_genomes_heterozygous": int(self.cleaned_data["thousand_genomes_heterozygous"])
            if self.cleaned_data["thousand_genomes_heterozygous"]
            else None,
            "effects": selected_effects,
            "genotype": list(),
            "gene_blacklist": [x.strip() for x in self.cleaned_data["gene_blacklist"].split()],
            "database_select": self.cleaned_data["database_select"],
            "exac_enabled": self.cleaned_data["exac_enabled"],
            "gnomad_exomes_enabled": self.cleaned_data["gnomad_exomes_enabled"],
            "gnomad_genomes_enabled": self.cleaned_data["gnomad_genomes_enabled"],
            "thousand_genomes_enabled": self.cleaned_data["thousand_genomes_enabled"],
            "var_type_snv": self.cleaned_data["var_type_snv"],
            "var_type_mnv": self.cleaned_data["var_type_mnv"],
            "var_type_indel": self.cleaned_data["var_type_indel"],
            "compound_recessive_enabled": self.cleaned_data["compound_recessive_enabled"],
            "pedigree": pedigree,
        }
        return kwargs

    def _build_query_args(self, kwargs):
        """Build the query from the postprocessed ``kwargs`` and the ``form`` instance."""
        for member in self.pedigree:
            gt = self.cleaned_data[member["fields"]["gt"]]

            kwargs["genotype"].append(
                {
                    "member": member["patient"],
                    "dp": self.cleaned_data[member["fields"]["dp"]],
                    "ad": self.cleaned_data[member["fields"]["ad"]],
                    "gq": self.cleaned_data[member["fields"]["gq"]],
                    "ab": self.cleaned_data[member["fields"]["ab"]],
                    "gt": FILTER_FORM_TRANSLATE_INHERITANCE[gt],
                    "fail": self.cleaned_data[member["fields"]["fail"]],
                }
            )

        qb = QueryBuilder()
        if kwargs["compound_recessive_enabled"]:
            return qb.build_comphet_query(kwargs, include_conservation=self.include_conservation)
        else:
            base = qb.build_base_query(kwargs, include_conservation=self.include_conservation)
            conditions = [
                qb.build_vartype_term(kwargs),
                qb.build_frequency_term(kwargs),
                qb.build_homozygous_term(kwargs),
                qb.build_heterozygous_term(kwargs),
                qb.build_case_term(kwargs),
                qb.build_effects_term(kwargs),
                qb.build_genotype_term_list(kwargs),
                qb.build_gene_blacklist_term(kwargs),
            ]
            return qb.build_top_level_query(base, conditions)

    def _transform_entry_interpret_database(self, kwargs, entry):
        """Transform result entry and set ``effect``, ``hgvs_p``, ``hgvs_c``, and
        ``transcript_coding`` attributes based on selecting RefSeq/ENSEMBL.
        """
        if kwargs["database_select"] == "refseq":
            entry.effect = set(entry.refseq_effect)
            entry.hgvs_p = entry.refseq_hgvs_p
            entry.hgvs_c = entry.refseq_hgvs_c
            entry.transcript_coding = entry.refseq_transcript_coding
        elif kwargs["database_select"] == "ensembl":
            entry.effect = set(entry.ensembl_effect)
            entry.hgvs_p = entry.ensembl_hgvs_p
            entry.hgvs_c = entry.ensembl_hgvs_c
            entry.transcript_coding = entry.ensembl_transcript_coding
        return entry

    def _transform_entry_gt_fields(self, entry):
        """Transform result entry and set ``gt``, ``dp``, ``ad``, ``gq``."""
        genotype_data = dict()
        dp_data = dict()
        ad_data = dict()
        gq_data = dict()
        for patient, data in entry.genotype.items():
            genotype_data[patient] = data["gt"]
            dp_data[patient] = data["dp"]
            ad_data[patient] = data["ad"]
            gq_data[patient] = data["gq"]
        entry.gt = genotype_data
        entry.dp = dp_data
        entry.ad = ad_data
        entry.gq = gq_data
        return entry

    def run(self):
        kwargs = self._build_query_kwargs()
        query, args = self._build_query_args(kwargs)

        entries = list(SmallVariant.objects.raw(query, args))
        for entry in entries:
            self._transform_entry_interpret_database(kwargs, entry)
            self._transform_entry_gt_fields(entry)
        return entries
