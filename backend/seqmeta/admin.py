from django.contrib import admin

from seqmeta.models import EnrichmentKit, TargetBedFile

# Register your models here.
admin.site.register(EnrichmentKit)
admin.site.register(TargetBedFile)
