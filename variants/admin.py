from django.contrib import admin

from .models import Case, SmallVariant, ExportFileBgJob, ExportFileJobResult, SmallVariantFlags

# Register your models here.
admin.site.register(Case)
admin.site.register(SmallVariant)
admin.site.register(ExportFileBgJob)
admin.site.register(ExportFileJobResult)
admin.site.register(SmallVariantFlags)
