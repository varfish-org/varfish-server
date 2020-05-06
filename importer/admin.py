from django.contrib import admin

from .models import (
    ImportInfo,
    CaseImportInfo,
    VariantSetImportInfo,
    BamQcFile,
    GenotypeFile,
    EffectFile,
    DatabaseInfoFile,
    ImportCaseBgJob,
)

# Register your models here.
admin.site.register(
    (
        ImportInfo,
        CaseImportInfo,
        VariantSetImportInfo,
        BamQcFile,
        GenotypeFile,
        EffectFile,
        DatabaseInfoFile,
        ImportCaseBgJob,
    )
)
