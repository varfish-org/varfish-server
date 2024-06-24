from django.contrib import admin

from seqvars.models import (
    SeqvarPresetsColumns,
    SeqvarPresetsConsequence,
    SeqvarPresetsFrequency,
    SeqvarPresetsLocus,
    SeqvarPresetsMisc,
    SeqvarPresetsPhenotypePrio,
    SeqvarPresetsVariantPrio,
    SeqvarQuery,
    SeqvarQueryExecution,
    SeqvarQueryPresetsSet,
    SeqvarQuerySettings,
    SeqvarResultRow,
    SeqvarResultSet,
)

admin.site.register(SeqvarQueryPresetsSet)
admin.site.register(SeqvarPresetsFrequency)
admin.site.register(SeqvarPresetsConsequence)
admin.site.register(SeqvarPresetsLocus)
admin.site.register(SeqvarPresetsPhenotypePrio)
admin.site.register(SeqvarPresetsVariantPrio)
admin.site.register(SeqvarPresetsColumns)
admin.site.register(SeqvarPresetsMisc)
admin.site.register(SeqvarQuerySettings)
admin.site.register(SeqvarQuery)
admin.site.register(SeqvarQueryExecution)
admin.site.register(SeqvarResultSet)
admin.site.register(SeqvarResultRow)
