from django.contrib import admin

from cases_files.models import ExternalFile, InternalFile

admin.site.register(ExternalFile)
admin.site.register(InternalFile)
