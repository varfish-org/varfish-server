from django.contrib import admin

from .models import (
    EnsemblRegulatoryFeature,
    GeneInterval,
    TadSet,
    TadInterval,
    TadBoundaryInterval,
    VistaEnhancer,
)

# Register your models here.
admin.site.register(EnsemblRegulatoryFeature)
admin.site.register(GeneInterval)
admin.site.register(TadSet)
admin.site.register(TadInterval)
admin.site.register(TadBoundaryInterval)
admin.site.register(VistaEnhancer)
