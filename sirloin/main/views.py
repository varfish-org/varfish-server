from itertools import product
from collections import defaultdict

from django.shortcuts import render, redirect
from django.views.generic import FormView, ListView, TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.forms.models import model_to_dict
from .forms import FilterForm
from .models import Main, Pedigree
from .models_support import (
    build_frequency_term,
    build_homozygous_term,
    build_case_term,
    build_effects_term,
    build_genotype_term_list,
    build_genotype_term,
    build_genotype_quality_term,
    build_genotype_ad_term,
    build_genotype_dp_term,
    build_genotype_gq_term,
    build_genotype_ab_term,
    build_genotype_gt_term,
    build_top_level_query,
)


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
                Pedigree.objects.get(case=self.kwargs["case"])
            )
        pedigree_object = self.pedigree_object

        index = pedigree_object["case"]

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
        pedigree = self.get_form_kwargs()["pedigree"]
        selected_effects = list()

        for field_name, effect in form.translate_effects.items():
            if form.cleaned_data[field_name]:
                selected_effects.append(effect)

        kwargs = {
            "case": self.kwargs["case"],
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
                    "gt": form.translate_inheritance[gt],
                    "fail": form.cleaned_data[member["fields"]["fail"]],
                }
            )

        conditions = [
            build_frequency_term(kwargs),
            build_homozygous_term(kwargs),
            build_case_term(kwargs),
            build_effects_term(kwargs),
            build_genotype_term_list(kwargs),
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


# for later with django F() operator
# reduce(operators.and_, conditions)

