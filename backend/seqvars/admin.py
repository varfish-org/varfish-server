from django.contrib import admin

from seqvars.models import (
    Query,
    QueryExecution,
    QueryPresetsFrequency,
    QueryPresetsSet,
    ResultRow,
    ResultSet,
)

admin.site.register(QueryPresetsSet)
admin.site.register(QueryPresetsFrequency)
admin.site.register(Query)
admin.site.register(QueryExecution)
admin.site.register(ResultSet)
admin.site.register(ResultRow)
