from django.contrib import admin

from .models import (
    BamQcFile,
    CaseGeneAnnotationFile,
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
        CaseGeneAnnotationFile,
        CaseImportInfo,
        VariantSetImportInfo,
        BamQcFile,
        GenotypeFile,
        EffectFile,
        DatabaseInfoFile,
        ImportCaseBgJob,
    )
)
