from django.contrib import admin

from .models import (
    CaddSubmissionBgJob,
    Case,
    CasePhenotypeTerms,
    DistillerSubmissionBgJob,
    ExportFileBgJob,
    ExportFileJobResult,
    FilterBgJob,
    ImportVariantsBgJob,
    ProjectCasesFilterBgJob,
    SmallVariant,
    SmallVariantComment,
    SmallVariantFlags,
    SmallVariantQuery,
    SmallVariantSet,
    SpanrSubmissionBgJob,
    SyncCaseListBgJob,
    SyncCaseResultMessage,
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
        SpanrSubmissionBgJob,
        CasePhenotypeTerms,
    )
)
