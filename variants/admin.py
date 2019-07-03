from django.contrib import admin

from .models import (
    Case,
    DistillerSubmissionBgJob,
    SmallVariant,
    ExportFileBgJob,
    ExportFileJobResult,
    SmallVariantFlags,
    SmallVariantQuery,
    SmallVariantComment,
    FilterBgJob,
    ProjectCasesFilterBgJob,
    ClinvarBgJob,
    SyncCaseListBgJob,
    SyncCaseResultMessage,
    ImportVariantsBgJob,
    SmallVariantSet,
)

# Register your models here.
admin.site.register(Case)
admin.site.register(SmallVariant)
admin.site.register(ExportFileBgJob)
admin.site.register(ExportFileJobResult)
admin.site.register(SmallVariantFlags)
admin.site.register(SmallVariantComment)
admin.site.register(SmallVariantQuery)
admin.site.register(DistillerSubmissionBgJob)
admin.site.register(FilterBgJob)
admin.site.register(ClinvarBgJob)
admin.site.register(ProjectCasesFilterBgJob)
admin.site.register(SyncCaseListBgJob)
admin.site.register(SyncCaseResultMessage)
admin.site.register(ImportVariantsBgJob)
admin.site.register(SmallVariantSet)
