from django.db.models import Q


def build_base_query():
    return r"""
        SELECT main_main.id, chromosome, position, reference, alternative,
            main_main.frequency, homozygous, main_main.effect, genotype,
            main_main.case_id, main_annotation.gene_name, main_pedigree.pedigree
        FROM main_main
        LEFT OUTER JOIN main_pedigree ON (main_main.case_id = main_pedigree.case)
        LEFT OUTER JOIN main_annotation USING (chromosome, position, reference, alternative)
    """


def build_frequency_term(kwargs):
    return "main_main.frequency <= {max_frequency}".format(**kwargs)


def build_homozygous_term(kwargs):
    return "homozygous = 0" if kwargs["remove_homozygous"] else "TRUE"


def build_case_term(kwargs):
    return "main_main.case_id = '{case}'".format(**kwargs)


def build_effects_term(kwargs):
    return "main_main.effect && ARRAY[{effects}]::VARCHAR[]".format(
        effects=",".join("'{}'".format(effect) for effect in kwargs["effects"])
    )


def build_genotype_term_list(kwargs):
    return " AND ".join(
        "({})".format(build_genotype_term(member))
        for member in kwargs["genotype"]
    )


def build_genotype_term(kwargs):
    if kwargs["fail"] == "drop-variant":
        tmpl = "{quality}"
        tmpl += " AND {gt}" if kwargs["gt"] else ""
    elif kwargs["fail"] == "no-call":
        tmpl = "NOT ({quality})"
        tmpl += " OR {gt}" if kwargs["gt"] else ""
    else:
        tmpl = "{gt}" if kwargs["gt"] else "TRUE"

    return tmpl.format(
        quality=build_genotype_quality_term(kwargs),
        gt=build_genotype_gt_term(kwargs),
    )


def build_genotype_quality_term(kwargs):
    return " AND ".join(
        "({})".format(x)
        for x in [
            build_genotype_ad_term(kwargs),
            build_genotype_dp_term(kwargs),
            build_genotype_gq_term(kwargs),
            build_genotype_ab_term(kwargs),
        ]
    )


def build_genotype_ad_term(kwargs):
    return "(genotype->'{member}'->'ad'->>1)::int >= {ad}".format(**kwargs)


def build_genotype_dp_term(kwargs):
    return "(genotype->'{member}'->>'dp')::int >= {dp}".format(**kwargs)


def build_genotype_gq_term(kwargs):
    return "(genotype->'{member}'->>'gq')::int >= {gq}".format(**kwargs)


def build_genotype_ab_term(kwargs):
    return (
        "(genotype->'{member}'->>'dp')::int != 0 "
        "AND {ab} <= ((genotype->'{member}'->'ad'->>1)::float / (genotype->'{member}'->>'dp')::float) "
        "AND ((genotype->'{member}'->'ad'->>1)::float / (genotype->'{member}'->>'dp')::float) <= 1 - {ab}"
    ).format(**kwargs)


def build_genotype_gt_term(kwargs):
    return "genotype->'{member}'->>'gt' = '{gt}'".format(**kwargs)


def build_top_level_query(conditions):
    conditions_joined = " AND ".join(
        "({})".format(condition) for condition in conditions
    )

    return "{base} WHERE {condition} ORDER BY chromosome, position".format(
        base=build_base_query(), condition=conditions_joined
    )
