from django.contrib import admin

from cases_files.models import (
    IndividualExternalFile,
    IndividualInternalFile,
    PedigreeExternalFile,
    PedigreeInternalFile,
)

admin.site.register(IndividualExternalFile)
admin.site.register(PedigreeExternalFile)
admin.site.register(IndividualInternalFile)
admin.site.register(PedigreeInternalFile)
