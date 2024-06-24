from django.contrib import admin

from .models import CaseAnalysis, CaseAnalysisSession

# Register your models here.
admin.site.register(CaseAnalysis)
admin.site.register(CaseAnalysisSession)
