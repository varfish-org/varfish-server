from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.generic import DetailView, FormView, ListView, View
import simplejson as json

from bgjobs.models import BackgroundJob
from clinvar.models import Clinvar
from conservation.models import KnowngeneAA
from frequencies.views import FrequencyMixin
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin
from querybuilder.models_support import QueryBuilder, FilterQueryRunner

from .models import Case, ExportFileBgJob
from .forms import FilterForm
from .tasks import export_file_task


class MainView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    template_name = "variants/case_select.html"
    permission_required = "variants.view_data"
    model = Case

    def get_queryset(self):
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])


class FilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    template_name = "variants/filter.html"
    permission_required = "variants.view_data"
    form_class = FilterForm
    success_url = "."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._case_object = None
        self._populator = None

    def get_case_object(self):
        if not self._case_object:
            self._case_object = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return self._case_object

    def get_populator(self, form):
        if not self._populator:
            self._populator = FilterQueryRunner(self.get_case_object(), form.cleaned_data)
        return self._populator

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["pedigree"] = list(FilterQueryRunner.build_pedigree(self.get_case_object()))
        return result

    def form_valid(self, form):
        """Main branching point either render result or create an asychronous job."""
        print(form.cleaned_data)
        if form.cleaned_data["submit"] == "download":
            return self._form_valid_file(form)
        else:
            return self._form_valid_render(form)

    def _form_valid_file(self, form):
        """The form is valid, we want to asynchronously build a file for later download."""
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for case {}".format(
                    form.cleaned_data["file_type"], self.get_case_object().name
                ),
                project=self._get_project(self.request, self.kwargs),
                job_type="variants.export_file_bg_job",
            )
            export_job = ExportFileBgJob.objects.create(
                project=self._get_project(self.request, self.kwargs),
                bg_job=bg_job,
                case=self.get_case_object(),
                query_args=json.dumps(form.cleaned_data),
                file_type=form.cleaned_data["file_type"],
            )
        messages.info(
            self.request,
            "Created background job for your file download. "
            "After the file has been generated, you will be able to download it here.",
        )
        export_file_task.delay(export_job_pk=export_job.pk)
        return redirect(export_job.get_absolute_url())

    def _form_valid_render(self, form):
        """The form is valid, we are supposed to render an HTML table with the results."""
        populator = self.get_populator(form)
        return render(self.request, self.template_name, self.get_context_data(main=populator.run()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case_name"] = self.get_case_object().name
        return context


class ExtendAPIView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FrequencyMixin,
    View,
):
    permission_required = "variants.view_data"

    def get(self, *args, **kwargs):
        self.kwargs = kwargs
        qb = QueryBuilder()

        key = {
            "release": self.kwargs["release"],
            "chromosome": self.kwargs["chromosome"],
            "position": self.kwargs["position"],
            "reference": self.kwargs["reference"],
            "alternative": self.kwargs["alternative"],
        }

        query = qb.build_knowngeneaa_query(self.kwargs)
        knowngeneaa = list(KnowngeneAA.objects.raw(*query))
        knowngeneaa_list = list()
        if len(knowngeneaa) > 0:
            for entry in knowngeneaa:
                knowngeneaa_list.append(
                    {
                        "chromosome": entry.chromosome,
                        "start": entry.start,
                        "end": entry.end,
                        "alignment": entry.alignment,
                    }
                )

        self.kwargs["knowngeneaa"] = knowngeneaa_list

        self.get_frequencies(fields=("af", "hom", "het"))

        try:
            filter_key = dict(key)
            filter_key["position"] = int(filter_key["position"]) - 1
            clinvar_list = list()
            clinvar = list(Clinvar.objects.filter(**filter_key))
            for entry in clinvar:
                clinvar_list.append(
                    {
                        "clinical_significance": entry.clinical_significance,
                        "all_traits": list({trait.lower() for trait in entry.all_traits}),
                    }
                )
            self.kwargs["clinvar"] = clinvar_list
            # response["clinvar"] = [model_to_dict(m) for m in clinvar]
        except ObjectDoesNotExist:
            self.kwargs["clinvar"] = None

        # return Response(response)
        return HttpResponse(json.dumps(self.kwargs), content_type="application/json")


class ExportFileJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the file export background job.
    """

    permission_required = "variants.view_data"
    template_name = "variants/export_job_view.html"
    model = ExportFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


class ExportFileJobDownloadView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Download the file generated, if generated.

    Otherwise, thrown 404.
    """

    http_method_names = ["get"]

    permission_required = "variants.view_data"
    template_name = "variants/export_job_view.html"
    model = ExportFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get(self, request, *args, **kwargs):
        try:
            content_types = {
                "tsv": " text/tab-separated-values",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
            obj = self.get_object()
            return HttpResponse(
                obj.export_result.payload, content_type=content_types[obj.file_type]
            )
        except ObjectDoesNotExist as e:
            raise Http404("File has not been generated (yet)!") from e
