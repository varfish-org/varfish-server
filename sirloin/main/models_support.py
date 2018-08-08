class QueryBuilder:
    def __init__(self):
        self.count = 0

    def _next_int(self):
        ret = self.count
        self.count += 1
        return ret

    def _next_name(self):
        return "name{}".format(self._next_int())

    def build_base_query(self):
        return r"""
            SELECT m.id, chromosome, position, reference, alternative, m.frequency,
                homozygous, m.effect, genotype, m.case_id, a.gene_name, p.pedigree
            FROM main_main m
            LEFT OUTER JOIN main_pedigree p USING (case_id)
            LEFT OUTER JOIN main_annotation a USING (
                chromosome,
                position,
                reference,
                alternative
            )
            """

    def build_frequency_term(self, kwargs):
        name = self._next_name()
        return (
            "m.frequency <= %({})s".format(name),
            {name: kwargs["max_frequency"]},
        )

    def build_homozygous_term(self, kwargs):
        return ("homozygous = 0" if kwargs["remove_homozygous"] else "TRUE", {})

    def build_case_term(self, kwargs):
        name = self._next_name()
        return ("m.case_id = %({})s".format(name), {name: kwargs["case_id"]})

    def build_effects_term(self, kwargs):
        args = {self._next_name(): effect for effect in kwargs["effects"]}
        effect_string = ",".join("%({})s".format(name) for name in args)
        return ("m.effect && ARRAY[{}]::VARCHAR[]".format(effect_string), args)

    def build_genotype_term_list(self, kwargs):
        query_list = list()
        args_merged = dict()
        for member in kwargs["genotype"]:
            query, args = self.build_genotype_term(member)
            query_list.append("({})".format(query))
            args_merged = {**args_merged, **args}
        return (" AND ".join(query_list), args_merged)

    def build_genotype_term(self, kwargs):
        quality_term, quality_args = self.build_genotype_quality_term(kwargs)
        gt_term, gt_args = self.build_genotype_gt_term(kwargs)

        if kwargs["fail"] == "drop-variant":
            tmpl = "{quality}"
            tmpl += " AND {gt}" if kwargs["gt"] else ""
        elif kwargs["fail"] == "no-call":
            tmpl = "NOT ({quality})"
            tmpl += " OR {gt}" if kwargs["gt"] else ""
        else:
            tmpl = "{gt}" if kwargs["gt"] else "TRUE"

        return (
            tmpl.format(quality=quality_term, gt=gt_term),
            {**gt_args, **quality_args},
        )

    def build_genotype_quality_term(self, kwargs):
        ad_term, ad_args = self.build_genotype_ad_term(kwargs)
        dp_term, dp_args = self.build_genotype_dp_term(kwargs)
        gq_term, gq_args = self.build_genotype_gq_term(kwargs)
        ab_term, ab_args = self.build_genotype_ab_term(kwargs)

        return (
            " AND ".join(
                "({})".format(x) for x in [ad_term, dp_term, gq_term, ab_term]
            ),
            {**ad_args, **dp_args, **gq_args, **ab_args},
        )

    def build_genotype_ad_term(self, kwargs):
        name1 = self._next_name()
        name2 = self._next_name()
        return (
            "(genotype->%({member})s->'ad'->>1)::int >= %({ad})s".format(
                member=name1, ad=name2
            ),
            {name1: kwargs["member"], name2: kwargs["ad"]},
        )

    def build_genotype_dp_term(self, kwargs):
        name1 = self._next_name()
        name2 = self._next_name()
        return (
            "(genotype->%({member})s->>'dp')::int >= %({dp})s".format(
                member=name1, dp=name2
            ),
            {name1: kwargs["member"], name2: kwargs["dp"]},
        )

    def build_genotype_gq_term(self, kwargs):
        name1 = self._next_name()
        name2 = self._next_name()
        return (
            "(genotype->%({member})s->>'gq')::int >= %({gq})s".format(
                member=name1, gq=name2
            ),
            {name1: kwargs["member"], name2: kwargs["gq"]},
        )

    def build_genotype_ab_term(self, kwargs):
        name1 = self._next_name()
        name2 = self._next_name()
        return (
            r"""
            ((genotype->%({member})s->>'dp')::int != 0)
            AND (%({ab})s <= ((genotype->%({member})s->'ad'->>1)::float / (genotype->%({member})s->>'dp')::float))
            AND (((genotype->%({member})s->'ad'->>1)::float / (genotype->%({member})s->>'dp')::float) <= (1 - %({ab})s))
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
        args[name_member] = kwargs["member"]
        term = " OR ".join(
            "genotype->%({member})s->>'gt' = %({gt})s".format(
                member=name_member, gt=gt
            )
            for gt in args
        )

        return (term, args)

    def build_top_level_query(self, conditions):
        condition_list = list()
        args_merged = dict()

        for condition, args in conditions:
            condition_list.append(condition)
            args_merged = {**args_merged, **args}

        conditions_joined = " AND ".join(
            "({})".format(condition) for condition in condition_list
        )

        return (
            "{base} WHERE {condition} ORDER BY chromosome, position".format(
                base=self.build_base_query(), condition=conditions_joined
            ),
            args_merged,
        )
