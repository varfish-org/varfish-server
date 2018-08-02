from itertools import product
from collections import defaultdict

from django.shortcuts import render, redirect
from django.views.generic import FormView, ListView, TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.forms.models import model_to_dict
from .forms import FilterForm
from .models import Main, Pedigree


TRANSLATE_INHERITANCE = {
    "any": None,
    "ref": ("0/0"),
    "het": ("0/1"),
    "hom": ("1/1"),
    "variant": ("0/1", "1/1"),
    "non-variant": ("0/0", "./."),
    "non-reference": ("0/1", "1/1", "./."),
}

TRANSLATE_EFFECTS = {
    "effect_coding_transcript_intron_variant": "coding_transcript_intron_variant",
    "effect_complex_substitution": "complex_substitution",
    "effect_direct_tandem_duplication": "direct_tandem_duplication",
    "effect_disruptive_inframe_deletion": "disruptive_inframe_deletion",
    "effect_disruptive_inframe_insertion": "disruptive_inframe_insertion",
    "effect_downstream_gene_variant": "downstream_gene_variant",
    "effect_feature_truncation": "feature_truncation",
    "effect_five_prime_UTR_exon_variant": "5_prime_UTR_exon_variant",
    "effect_five_prime_UTR_intron_variant": "5_prime_UTR_intron_variant",
    "effect_frameshift_elongation": "frameshift_elongation",
    "effect_frameshift_truncation": "frameshift_truncation",
    "effect_frameshift_variant": "frameshift_variant",
    "effect_inframe_deletion": "inframe_deletion",
    "effect_inframe_insertion": "inframe_insertion",
    "effect_intergenic_variant": "intergenic_variant",
    "effect_internal_feature_elongation": "internal_feature_elongation",
    "effect_missense_variant": "missense_variant",
    "effect_mnv": "mnv",
    "effect_non_coding_transcript_exon_variant": "non_coding_transcript_exon_variant",
    "effect_non_coding_transcript_intron_variant": "non_coding_transcript_intron_variant",
    "effect_splice_acceptor_variant": "splice_acceptor_variant",
    "effect_splice_donor_variant": "splice_donor_variant",
    "effect_splice_region_variant": "splice_region_variant",
    "effect_start_lost": "start_lost",
    "effect_stop_gained": "stop_gained",
    "effect_stop_lost": "stop_lost",
    "effect_stop_retained_variant": "stop_retained_variant",
    "effect_structural_variant": "structural_variant",
    "effect_synonymous_variant": "synonymous_variant",
    "effect_three_prime_UTR_exon_variant": "3_prime_UTR_exon_variant",
    "effect_three_prime_UTR_intron_variant": "3_prime_UTR_intron_variant",
    "effect_transcript_ablation": "transcript_ablation",
    "effect_upstream_gene_variant": "upstream_gene_variant",
}


class MainView(ListView):
    template_name = "main/case_select.html"
    model = Pedigree

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class FilterView(FormView):
    template_name = "main/filter.html"
    form_class = FilterForm
    success_url = "."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pedigree_object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if not self.pedigree_object:
            self.pedigree_object = model_to_dict(
                Pedigree.objects.get(case_id=self.kwargs["case_id"])
            )
        pedigree_object = self.pedigree_object

        index = pedigree_object["case_id"]

        for member in pedigree_object["pedigree"]:
            if member["patient"] == index:
                father = member["father"]
                mother = member["mother"]

        kwargs["pedigree"] = list()
        for member in pedigree_object["pedigree"]:
            member = member["patient"]
            if member == father:
                role = "father"
            elif member == index:
                role = "index"
            elif member == mother:
                role = "mother"
            else:
                role = ""
            kwargs["pedigree"].append(
                {
                    "patient": member,
                    "role": role,
                    "fields": {
                        "gt": "%s_gt" % member,
                        "dp": "%s_dp" % member,
                        "ab": "%s_ab" % member,
                        "gq": "%s_gq" % member,
                        "ad": "%s_ad" % member,
                        "fail": "%s_fail" % member,
                    },
                }
            )

        return kwargs

    def form_valid(self, form):
        # case = self.kwargs["case_id"]
        pedigree = self.get_form_kwargs()["pedigree"]
        # max_frequency = form.cleaned_data["frequency_filter"]
        # remove_homozygous = form.cleaned_data["remove_homozygous"]
        selected_effects = list()

        for field_name, effect in TRANSLATE_EFFECTS.items():
            if form.cleaned_data[field_name]:
                selected_effects.append(effect)

        # GT_TEMPLATE = "genotype->'{}'->>'gt' = '{}'"
        # AD_TEMPLATE = "(genotype->'{}'->'ad'->>1)::int >= {}"
        # DP_TEMPLATE = "(genotype->'{}'->>'dp')::int >= {}"
        # GQ_TEMPLATE = "(genotype->'{}'->>'gq')::int >= {}"
        # AB_TEMPLATE = (
        #     "(genotype->'{m}'->>'dp')::int != 0 "
        #     "AND {ab} <= ((genotype->'{m}'->'ad'->>1)::float / (genotype->'{m}'->>'dp')::float) "
        #     "AND ((genotype->'{m}'->'ad'->>1)::float / (genotype->'{m}'->>'dp')::float) <= 1 - {ab}"
        # )

        # conditions = list()

        kwargs = {
            "case_id": self.kwargs["case_id"],
            "max_frequency": form.cleaned_data["frequency_filter"],
            "remove_homozygous": form.cleaned_data["remove_homozygous"],
            "effects": selected_effects,
            "genotype": list(),
        }

        for member in pedigree:
            gt = form.cleaned_data[member["fields"]["gt"]]

            kwargs["genotype"].append(
                {
                    "member": member["patient"],
                    "dp": form.cleaned_data[member["fields"]["dp"]],
                    "ad": form.cleaned_data[member["fields"]["ad"]],
                    "gq": form.cleaned_data[member["fields"]["gq"]],
                    "ab": form.cleaned_data[member["fields"]["ab"]],
                    "gt": TRANSLATE_INHERITANCE[gt],
                    "fail": form.cleaned_data[member["fields"]["fail"]],
                }
            )

            # condition = (
            #     DP_TEMPLATE.format(
            #         member["patient"], form.cleaned_data[member["fields"]["dp"]]
            #     )
            #     + " AND "
            #     + AD_TEMPLATE.format(
            #         member["patient"], form.cleaned_data[member["fields"]["ad"]]
            #     )
            #     + " AND "
            #     + GQ_TEMPLATE.format(
            #         member["patient"], form.cleaned_data[member["fields"]["gq"]]
            #     )
            #     + " AND "
            #     + AB_TEMPLATE.format(
            #         m=member["patient"],
            #         ab=form.cleaned_data[member["fields"]["ab"]],
            #     )
            # )

            # condition_string = ""
            # gt_condition = ""
            # if not gt_setting == "any":
            #     gt_condition = GT_TEMPLATE.format(
            #         member["patient"], TRANSLATE_INHERITANCE[gt_setting]
            #     )

            # if fail_setting == "drop-variant":
            #     condition_string = condition
            #     if gt_condition:
            #         condition_string += " AND " + gt_condition
            # elif fail_setting == "no-call":
            #     condition_string = " NOT (" + condition + ")"
            #     if gt_condition:
            #         condition_string += " OR " + gt_condition
            # else:
            #     if gt_condition:
            #         condition_string = gt_condition

            # if condition_string:
            #     conditions.append("(" + condition_string + ")")

        conditions = [
            build_frequency_term(kwargs),
            build_homozygous_term(kwargs),
            build_case_term(kwargs),
            build_effects_term(kwargs),
            build_genotype_terms(kwargs),
        ]

        query = build_top_level_query(conditions)
        main = list(Main.objects.raw(query))

        for entry in main:
            entry.effect = set(entry.effect) & set(selected_effects)
            genotype_data = dict()
            for patient, data in entry.genotype.items():
                genotype_data[patient] = data["gt"]

            entry.gt = genotype_data

        return render(
            self.request, self.template_name, self.get_context_data(main=main)
        )


def build_base_query():
    return r"""
        SELECT main_main.id, chromosome, position, reference, alternative,
            main_main.frequency, homozygous, main_main.effect, genotype,
            main_main.case_id, main_annotation.gene_name, main_pedigree.pedigree
        FROM main_main
        LEFT OUTER JOIN main_pedigree USING (case_id)
        LEFT OUTER JOIN main_annotation USING (chromosome, position, reference, alternative)
    """


def build_frequency_term(kwargs):
    return "main_main.frequency <= {max_frequency}".format(
        max_frequency=kwargs["max_frequency"]
    )


def build_homozygous_term(kwargs):
    return "homozygous = 0" if kwargs["remove_homozygous"] else None


def build_case_term(kwargs):
    return "case_id = '{case_id}'".format(case_id=kwargs["case_id"])


def build_effects_term(kwargs):
    return "main_main.effect && ARRAY[{effects}]::VARCHAR[]".format(
        effects=",".join("'{}'".format(effect) for effect in kwargs["effects"])
    )


def build_genotype_terms(kwargs):
    genotype_terms = filter_empty_terms(
        build_genotype_term(x) for x in kwargs["genotype"]
    )
    return " AND ".join("({})".format(x) for x in genotype_terms)


def build_genotype_term(kwargs):
    if kwargs["fail"] == "drop-variant":
        tmpl = "{quality}"
        if kwargs["gt"]:
            tmpl += " AND {gt}"
    elif kwargs["fail"] == "no-call":
        tmpl = "NOT ({quality})"
        if kwargs["gt"]:
            tmpl += " OR {gt}"
    else:
        if kwargs["gt"]:
            tmpl = "{gt}"
        else:
            tmpl = ""

    return tmpl.format(
        quality=build_genotype_quality_term(kwargs),
        gt=build_genotype_gt_term(kwargs),
    )


def build_genotype_quality_term(kwargs):
    return " AND ".join(
        [
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
        "({})".format(condition) for condition in filter_empty_terms(conditions)
    )

    return "{base} WHERE {condition} ORDER BY chromosome, position".format(
        base=build_base_query(), condition=conditions_joined
    )


def filter_empty_terms(terms):
    return [term for term in terms if term]


# for later with django F() operator
# reduce(operators.and_, conditions)

