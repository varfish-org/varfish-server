from django.contrib import admin

from .models import DbVarSv, DgvGoldStandardSvs, DgvSvs, ExacCnv, ThousandGenomesSv

# Register your models here.
admin.site.register(DgvGoldStandardSvs)
admin.site.register(DgvSvs)
admin.site.register(DbVarSv)
admin.site.register(ThousandGenomesSv)
admin.site.register(ExacCnv)
