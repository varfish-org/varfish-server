from django.contrib import admin

from .models import (
    Case,
    CaddSubmissionBgJob,
    DistillerSubmissionBgJob,
    SmallVariant,
    ExportFileBgJob,
    ExportFileJobResult,
    SmallVariantFlags,
    SmallVariantQuery,
    SmallVariantComment,
    FilterBgJob,
    ProjectCasesFilterBgJob,
    SyncCaseListBgJob,
    SyncCaseResultMessage,
    ImportVariantsBgJob,
    SmallVariantSet,
)

# Register your models here.
admin.site.register(
    (
        Case,
        CaddSubmissionBgJob,
        DistillerSubmissionBgJob,
        SmallVariant,
        ExportFileBgJob,
        ExportFileJobResult,
        SmallVariantFlags,
        SmallVariantQuery,
        SmallVariantComment,
        FilterBgJob,
        ProjectCasesFilterBgJob,
        SyncCaseListBgJob,
        SyncCaseResultMessage,
        ImportVariantsBgJob,
        SmallVariantSet,
    )
)
