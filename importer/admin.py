from django.contrib import admin

from .models import (
    BamQcFile,
    CaseImportInfo,
    DatabaseInfoFile,
    EffectFile,
    GenotypeFile,
    ImportCaseBgJob,
    ImportInfo,
    VariantSetImportInfo,
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
