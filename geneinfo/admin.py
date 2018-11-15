from django.contrib import admin

from .models import Hgnc, Mim2geneMedgen, Hpo

# Register your models here.
admin.site.register(Hgnc)
admin.site.register(Mim2geneMedgen)
admin.site.register(Hpo)
