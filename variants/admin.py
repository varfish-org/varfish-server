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
