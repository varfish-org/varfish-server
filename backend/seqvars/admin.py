from django.contrib import admin

from seqvars.models import (
    SeqvarPresetsFrequency,
    SeqvarQuery,
    SeqvarQueryExecution,
    SeqvarQueryPresetsSet,
    SeqvarResultRow,
    SeqvarResultSet,
)

admin.site.register(SeqvarQueryPresetsSet)
admin.site.register(SeqvarPresetsFrequency)
admin.site.register(SeqvarQuery)
admin.site.register(SeqvarQueryExecution)
admin.site.register(SeqvarResultSet)
admin.site.register(SeqvarResultRow)
