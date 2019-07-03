from django.contrib import admin


from .models import (
    StructuralVariant,
    StructuralVariantGeneAnnotation,
    StructuralVariantFlags,
    StructuralVariantComment,
    ImportStructuralVariantBgJob,
    StructuralVariantSet,
)

# Register your models here.
admin.site.register(StructuralVariant)
admin.site.register(StructuralVariantGeneAnnotation)
admin.site.register(StructuralVariantFlags)
admin.site.register(StructuralVariantComment)
admin.site.register(StructuralVariantSet)
admin.site.register(ImportStructuralVariantBgJob)
