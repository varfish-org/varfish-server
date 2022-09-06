"""URL configuration for the ``clinvar_export`` app."""

from django.conf.urls import url

from . import views, views_ajax

app_name = "clinvar_export"

ui_urlpatterns = [
    # Vue.js entrypoint
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/$",
        view=views.SubmissionSetView.as_view(),
        name="entrypoint",
    ),
]

ajax_urlpatterns = [
    # AJAX API views
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/organisation/$",
        view=views_ajax.OrganisationReadView.as_view(),
        name="ajax-organisation-list",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/submitter/$",
        view=views_ajax.SubmitterReadView.as_view(),
        name="ajax-submitter-list",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/assertionmethod/$",
        view=views_ajax.AssertionMethodReadView.as_view(),
        name="ajax-assertionmethod-list",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/submissionset/$",
        view=views_ajax.SubmissionSetListCreateView.as_view(),
        name="ajax-submissionset-list-create",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/submissionset/(?P<submissionset>[0-9a-f-]+)/$",
        view=views_ajax.SubmissionSetRetrieveUpdateDestroyView.as_view(),
        name="ajax-submissionset-retrieve-update-destroy",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/clinvar-xml/(?P<submissionset>[0-9a-f-]+)/$",
        view=views_ajax.SubmissionSetRenderClinvarXml.as_view(),
        name="ajax-submissionset-clinvar-xml",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/clinvar-validate/(?P<submissionset>[0-9a-f-]+)/$",
        view=views_ajax.SubmissionSetValidateClinvarXml.as_view(),
        name="ajax-submissionset-clinvar-validate",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/submission/$",
        view=views_ajax.SubmissionListCreateView.as_view(),
        name="ajax-submission-list-create",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/submission/(?P<submission>[0-9a-f-]+)/$",
        view=views_ajax.SubmissionRetrieveUpdateDestroyView.as_view(),
        name="ajax-submission-retrieve-update-destroy",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/submissionindividual/$",
        view=views_ajax.SubmissionIndividualListCreateView.as_view(),
        name="ajax-submissionindividual-list-create",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/submissionindividual/(?P<submissionindividual>[0-9a-f-]+)/$",
        view=views_ajax.SubmissionIndividualRetrieveUpdateDestroyView.as_view(),
        name="ajax-submissionindividual-retrieve-update-destroy",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/individual/$",
        view=views_ajax.IndividualReadView.as_view(),
        name="ajax-individual-list",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/family/$",
        view=views_ajax.FamilyReadView.as_view(),
        name="ajax-family-list",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/submittingorg/$",
        view=views_ajax.SubmittingOrgListCreateView.as_view(),
        name="ajax-submittingorg-list-create",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/submittingorg/(?P<submittingorg>[0-9a-f-]+)/$",
        view=views_ajax.SubmittingOrgRetrieveUpdateDestroyView.as_view(),
        name="ajax-submittingorg-retrieve-update-destroy",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/query-omim/?$",
        view=views_ajax.QueryOmimTermApiView.as_view(),
        name="query-omim-term",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/query-hpo/?$",
        view=views_ajax.QueryHpoTermApiView.as_view(),
        name="query-hpo-term",
    ),
    url(
        regex=r"^ajax/(?P<project>[0-9a-f-]+)/user-annotations/(?P<family>[0-9a-f-]+)/?$",
        view=views_ajax.AnnotatedSmallVariantsApiView.as_view(),
        name="user-annotations",
    ),
]

urlpatterns = ui_urlpatterns + ajax_urlpatterns
