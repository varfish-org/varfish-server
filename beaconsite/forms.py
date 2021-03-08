from django import forms
from django.db import transaction
from projectroles.models import Project

from .models import Consortium, Site, ConsortiumMember, ConsortiumAssignment


class ConsortiumForm(forms.ModelForm):
    class Meta:
        model = Consortium
        fields = ("title", "identifier", "description", "state")

    sites = forms.ModelMultipleChoiceField(
        queryset=Site.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )

    def __init__(self, *args, **kwargs):
        if kwargs.get("instance"):
            initial = kwargs.setdefault("initial", {})
            initial["sites"] = [t.pk for t in kwargs["instance"].sites.all()]
            initial["projects"] = [t.pk for t in kwargs["instance"].projects.all()]

        forms.ModelForm.__init__(self, *args, **kwargs)

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save(False)

        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            # Site assignment
            current_s = {m.site_id for m in ConsortiumMember.objects.filter(consortium=instance)}
            wanted_s = {s.pk for s in self.cleaned_data["sites"]}
            for pk in wanted_s - current_s:
                ConsortiumMember.objects.create(consortium=instance, site=Site.objects.get(pk=pk))
            for pk in current_s - wanted_s:
                ConsortiumMember.objects.filter(
                    consortium=instance, site=Site.objects.get(pk=pk)
                ).delete()
            # Project assignment
            current_p = {
                m.project_id for m in ConsortiumAssignment.objects.filter(consortium=instance)
            }
            wanted_p = {s.pk for s in self.cleaned_data["projects"]}
            for pk in wanted_p - current_p:
                ConsortiumAssignment.objects.create(
                    consortium=instance, project=Project.objects.get(pk=pk)
                )
            for pk in current_p - wanted_p:
                ConsortiumAssignment.objects.filter(
                    consortium=instance, project=Project.objects.get(pk=pk)
                ).delete()

        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = (
            "title",
            "identifier",
            "description",
            "state",
            "role",
            "entrypoint_url",
            "key_algo",
            "private_key",
            "public_key",
        )

    entrypoint_url = forms.CharField()
    consortia = forms.ModelMultipleChoiceField(
        queryset=Consortium.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )

    def __init__(self, *args, **kwargs):
        if kwargs.get("instance"):
            initial = kwargs.setdefault("initial", {})
            initial["consortia"] = [t.pk for t in kwargs["instance"].consortia.all()]

        forms.ModelForm.__init__(self, *args, **kwargs)

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save(False)

        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            # Consortia assignment
            current_c = {m.consortium_id for m in ConsortiumMember.objects.filter(site=instance)}
            wanted_c = {s.pk for s in self.cleaned_data["consortia"]}
            for pk in wanted_c - current_c:
                ConsortiumMember.objects.create(
                    site=instance, consortium=Consortium.objects.get(pk=pk)
                )
            for pk in current_c - wanted_c:
                ConsortiumMember.objects.filter(
                    site=instance, consortium=Consortium.objects.get(pk=pk)
                ).delete()

        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance
