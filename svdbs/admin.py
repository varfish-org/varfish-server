from django.contrib import admin

from .models import DgvGoldStandardSvs, DgvSvs, DbVarSv, ThousandGenomesSv, ExacCnv

# Register your models here.
admin.site.register(DgvGoldStandardSvs)
admin.site.register(DgvSvs)
admin.site.register(DbVarSv)
admin.site.register(ThousandGenomesSv)
admin.site.register(ExacCnv)
