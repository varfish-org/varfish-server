import json

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, RedirectView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .forms import FilterForm
from .models import Main, Annotation, Exac, Hgnc, Hpo, Mim2geneMedgen


class MainView(FormView):
    template_name = "main/main.html"
    form_class = FilterForm
    success_url = "."

    def post(self, request):
        filterform = FilterForm(request.POST)
        accepted_effects = [
            "splice_acceptor_variant",
            "splice_donor_variant",
            "splice_region_variant",
            "missense_variant",
        ]

        if filterform.is_valid():
            max_frequency = filterform.cleaned_data["frequency_filter"]
            cases = [case.case_id for case in filterform.cleaned_data["cases"]]
            remove_homozygous = filterform.cleaned_data["remove_homozygous"]
            # main = Main.objects.select_related().filter(
            #     frequency__lte=max_frequency,
            #     homozygous=0,
            #     effect__overlap=accepted_effects,
            #     case_id__in=cases,
            # )

            _accepted_effects = ",".join(
                ["'" + effect + "'" for effect in accepted_effects]
            )
            _cases = ",".join(["'" + case + "'" for case in cases])
            main = Main.objects.raw(
                (
                    "SELECT main_main.id, chromosome, position, reference, alternative, main_main.frequency, homozygous, main_main.effect, genotype, main_main.case_id, main_pedigree.pedigree FROM main_main "
                    "LEFT OUTER JOIN main_pedigree USING (case_id) "
                    "WHERE main_main.frequency < {max_frequency} "
                    "{homozygous} "
                    "AND case_id IN ({cases}) "
                    "AND (main_main.effect && ARRAY[{effects}]::VARCHAR[])"
                ).format(
                    max_frequency=max_frequency,
                    homozygous="AND homozygous = 0"
                    if remove_homozygous
                    else "",
                    effects=_accepted_effects,
                    cases=_cases,
                )
            )

            def curate(main):
                for entry in main:
                    entry.effect = set(entry.effect) & set(accepted_effects)
                    for member in entry.pedigree:
                        if member["patient"] == entry.case_id:
                            father = member["father"]
                            mother = member["mother"]
                    entry.gt_index = entry.genotype[entry.case_id]
                    entry.gt_mother = (
                        entry.genotype[mother] if not mother == "0" else None
                    )
                    entry.gt_father = (
                        entry.genotype[father] if not father == "0" else None
                    )
                    yield entry

            return render(
                request,
                self.template_name,
                {
                    "hom": remove_homozygous,
                    "main": curate(main),
                    "form": FilterForm(
                        data={
                            "frequency_filter": max_frequency,
                            "cases": cases,
                            "remove_homozygous": remove_homozygous,
                        }
                    ),
                },
            )
