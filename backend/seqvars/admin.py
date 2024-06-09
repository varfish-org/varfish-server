from django.contrib import admin

from seqvars.models import (
    SeqvarColumnPresets,
    SeqvarConsequencePresets,
    SeqvarFrequencyPresets,
    SeqvarLocusPresets,
    SeqvarMiscPresets,
    SeqvarPhenotypePrioPresets,
    SeqvarPresetsBase,
    SeqvarQuery,
    SeqvarQueryExecution,
    SeqvarQueryPresetsSet,
    SeqvarQuerySettings,
    SeqvarResultSet,
    SeqvarResultSetRow,
    SeqvarVariantPrioPresets,
)

admin.site.register(SeqvarQueryPresetsSet)
admin.site.register(SeqvarPresetsBase)
admin.site.register(SeqvarFrequencyPresets)
admin.site.register(SeqvarConsequencePresets)
admin.site.register(SeqvarLocusPresets)
admin.site.register(SeqvarPhenotypePrioPresets)
admin.site.register(SeqvarVariantPrioPresets)
admin.site.register(SeqvarColumnPresets)
admin.site.register(SeqvarMiscPresets)
admin.site.register(SeqvarQuerySettings)
admin.site.register(SeqvarQuery)
admin.site.register(SeqvarQueryExecution)
admin.site.register(SeqvarResultSet)
admin.site.register(SeqvarResultSetRow)
