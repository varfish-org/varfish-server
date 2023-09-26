from django.contrib import admin

from cases_import.models.base import CaseImportAction, CaseImportBackgroundJob

admin.site.register(CaseImportAction)
admin.site.register(CaseImportBackgroundJob)
