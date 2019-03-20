from django.contrib import admin

from .models import (
    Hgnc,
    Mim2geneMedgen,
    Hpo,
    Acmg,
    HpoName,
    NcbiGeneInfo,
    NcbiGeneRif,
    RefseqToHgnc,
)

# Register your models here.
admin.site.register(Hgnc)
admin.site.register(Mim2geneMedgen)
admin.site.register(Hpo)
admin.site.register(Acmg)
admin.site.register(HpoName)
admin.site.register(NcbiGeneInfo)
admin.site.register(NcbiGeneRif)
admin.site.register(RefseqToHgnc)
