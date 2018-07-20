from django import forms
from .models import Pedigree


class FilterForm(forms.Form):
    frequency_filter = forms.FloatField(
        initial=0.01,
        max_value=0.01,
        min_value=0,
        widget=forms.NumberInput(attrs={"step": "0.001"}),
    )
    remove_homozygous = forms.BooleanField(
        label="Remove homozygous variants",
        required=False,
    )
    remove_intergenic = forms.BooleanField(
        label="Remove intergenic and deep intronic variants",
        required=True,
        initial=True,
        disabled=True,
    )
    cases = forms.ModelMultipleChoiceField(
        queryset=Pedigree.objects.all(), to_field_name="case_id"
    )
