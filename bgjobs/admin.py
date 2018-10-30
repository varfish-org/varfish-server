from django.contrib import admin

from .models import BackgroundJob, BackgroundJobLogEntry

# Register your models here.
admin.site.register(BackgroundJob)
admin.site.register(BackgroundJobLogEntry)
