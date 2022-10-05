from django.contrib import admin

from .models import GenePanel, GenePanelCategory, GenePanelEntry

# Register your models here.
admin.site.register(GenePanelCategory)
admin.site.register(GenePanel)
admin.site.register(GenePanelEntry)
