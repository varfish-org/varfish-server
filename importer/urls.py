"""URL configuration for the ``importer`` app.
"""

from django.conf.urls import url
from . import views, views_api

app_name = "importer"

ui_urlpatterns = [
    url(regex=r"^import-info$", view=views.ImportInfoView.as_view(), name="import-info"),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/import/(?P<job>[0-9a-f-]+)/$",
        view=views.ImportCaseBgJobDetailView.as_view(),
        name="import-case-job-detail",
    ),
]

api_urlpatterns = [
    url(
        regex=r"^api/case-import-info/(?P<project>[0-9a-f-]+)/$",
        view=views_api.CaseImportInfoListCreateView.as_view(),
        name="api-case-import-info-list-create",
    ),
    url(
        regex=r"^api/case-import-info/(?P<project>[0-9a-f-]+)/(?P<case_import_info>[0-9a-f-]+)/$",
        view=views_api.CaseImportInfoRetrieveUpdateDestroyView.as_view(),
        name="api-case-import-info-retrieve-update-destroy",
    ),
    url(
        regex=r"^api/variant-set-import-info/(?P<case_import_info>[0-9a-f-]+)/$",
        view=views_api.VariantSetImportInfoListCreateView.as_view(),
        name="api-variant-set-import-info-list-create",
    ),
    url(
        regex=r"^api/variant-set-import-info/(?P<case_import_info>[0-9a-f-]+)/(?P<variant_set_import_info>[0-9a-f-]+)/$",
        view=views_api.VariantSetImportInfoRetrieveUpdateDestroyView.as_view(),
        name="api-variant-set-import-info-retrieve-update-destroy",
    ),
    url(
        regex=r"^api/bam-qc-file/(?P<case_import_info>[0-9a-f-]+)/$",
        view=views_api.BamQcFileListCreateView.as_view(),
        name="api-bam-qc-file-list-create",
    ),
    url(
        regex=r"^api/bam-qc-file/(?P<case_import_info>[0-9a-f-]+)/(?P<bam_qc_file>[0-9a-f-]+)/$",
        view=views_api.BamQcFileRetrieveDestroyView.as_view(),
        name="api-bam-qc-file-retrieve-destroy",
    ),
    url(
        regex=r"^api/genotype-file/(?P<variant_set_import_info>[0-9a-f-]+)/$",
        view=views_api.GenotypeFileListCreateView.as_view(),
        name="api-genotype-file-list-create",
    ),
    url(
        regex=r"^api/genotype-file/(?P<variant_set_import_info>[0-9a-f-]+)/(?P<genotype_file>[0-9a-f-]+)/$",
        view=views_api.GenotypeFileRetrieveDestroyView.as_view(),
        name="api-genotype-file-retrieve-destroy",
    ),
    url(
        regex=r"^api/effects-file/(?P<variant_set_import_info>[0-9a-f-]+)/$",
        view=views_api.EffectsFileListCreateView.as_view(),
        name="api-effects-file-list-create",
    ),
    url(
        regex=r"^api/effects-file/(?P<variant_set_import_info>[0-9a-f-]+)/(?P<effects_file>[0-9a-f-]+)/$",
        view=views_api.EffectsFileRetrieveDestroyView.as_view(),
        name="api-effects-file-retrieve-destroy",
    ),
    url(
        regex=r"^api/database-info-file/(?P<variant_set_import_info>[0-9a-f-]+)/$",
        view=views_api.DatabaseInfoFileListCreateView.as_view(),
        name="api-db-info-file-list-create",
    ),
    url(
        regex=r"^api/database-info-file/(?P<variant_set_import_info>[0-9a-f-]+)/(?P<database_info_file>[0-9a-f-]+)/$",
        view=views_api.DatabaseInfoFileRetrieveDestroyView.as_view(),
        name="api-db-info-file-retrieve-destroy",
    ),
]

urlpatterns = ui_urlpatterns + api_urlpatterns
