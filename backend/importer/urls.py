"""URL configuration for the ``importer`` app.
"""

from django.urls import path

from . import views, views_api

app_name = "importer"

ui_urlpatterns = [
    path("import-info/", view=views.ImportInfoView.as_view(), name="import-info"),
    path(
        "<uuid:project>/import/<uuid:job>/",
        view=views.ImportCaseBgJobDetailView.as_view(),
        name="import-case-job-detail",
    ),
]

api_urlpatterns = [
    path(
        "api/case-import-info/<uuid:project>/",
        view=views_api.CaseImportInfoListCreateView.as_view(),
        name="api-case-import-info-list-create",
    ),
    path(
        "api/case-import-info/<uuid:project>/<uuid:caseimportinfo>/",
        view=views_api.CaseImportInfoRetrieveUpdateDestroyView.as_view(),
        name="api-case-import-info-retrieve-update-destroy",
    ),
    path(
        "api/variant-set-import-info/<uuid:caseimportinfo>/",
        view=views_api.VariantSetImportInfoListCreateView.as_view(),
        name="api-variant-set-import-info-list-create",
    ),
    path(
        "api/variant-set-import-info/<uuid:caseimportinfo>/<uuid:variantsetimportinfo>/",
        view=views_api.VariantSetImportInfoRetrieveUpdateDestroyView.as_view(),
        name="api-variant-set-import-info-retrieve-update-destroy",
    ),
    path(
        "api/bam-qc-file/<uuid:caseimportinfo>/",
        view=views_api.BamQcFileListCreateView.as_view(),
        name="api-bam-qc-file-list-create",
    ),
    path(
        "api/bam-qc-file/<uuid:caseimportinfo>/<uuid:bamqcfile>/",
        view=views_api.BamQcFileRetrieveDestroyView.as_view(),
        name="api-bam-qc-file-retrieve-destroy",
    ),
    path(
        "api/case-gene-annotation-file/<uuid:caseimportinfo>/",
        view=views_api.CaseGeneAnnotationFileListCreateView.as_view(),
        name="api-case-gene-annotation-file-list-create",
    ),
    path(
        "api/case-gene-annotation-file/<uuid:caseimportinfo>/<uuid:casegeneannotationfile>/",
        view=views_api.CaseGeneAnnotationFileRetrieveDestroyView.as_view(),
        name="api-case-gene-annotation-file-retrieve-destroy",
    ),
    path(
        "api/genotype-file/<uuid:variantsetimportinfo>/",
        view=views_api.GenotypeFileListCreateView.as_view(),
        name="api-genotype-file-list-create",
    ),
    path(
        "api/genotype-file/<uuid:variantsetimportinfo>/<uuid:genotypefile>/",
        view=views_api.GenotypeFileRetrieveDestroyView.as_view(),
        name="api-genotype-file-retrieve-destroy",
    ),
    path(
        "api/effects-file/<uuid:variantsetimportinfo>/",
        view=views_api.EffectsFileListCreateView.as_view(),
        name="api-effects-file-list-create",
    ),
    path(
        "api/effects-file/<uuid:variantsetimportinfo>/<uuid:effectsfile>/",
        view=views_api.EffectsFileRetrieveDestroyView.as_view(),
        name="api-effects-file-retrieve-destroy",
    ),
    path(
        "api/database-info-file/<uuid:variantsetimportinfo>/",
        view=views_api.DatabaseInfoFileListCreateView.as_view(),
        name="api-db-info-file-list-create",
    ),
    path(
        "api/database-info-file/<uuid:variantsetimportinfo>/<uuid:databaseinfofile>/",
        view=views_api.DatabaseInfoFileRetrieveDestroyView.as_view(),
        name="api-db-info-file-retrieve-destroy",
    ),
]

urlpatterns = ui_urlpatterns + api_urlpatterns
