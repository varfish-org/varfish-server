from django.contrib import admin

from seqvars.models import (
    SeqvarsQuery,
    SeqvarsQueryExecution,
    SeqvarsQueryPresetsFrequency,
    SeqvarsQueryPresetsSet,
    SeqvarsResultRow,
    SeqvarsResultSet,
)

admin.site.register(SeqvarsQueryPresetsSet)
admin.site.register(SeqvarsQueryPresetsFrequency)
admin.site.register(SeqvarsQuery)
admin.site.register(SeqvarsQueryExecution)
admin.site.register(SeqvarsResultSet)
admin.site.register(SeqvarsResultRow)
