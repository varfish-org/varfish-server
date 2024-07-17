from django.contrib import admin

from .models import SmallVariantQueryGestaltMatcherScores, SmallVariantQueryPediaScores

# Register your models here.
admin.site.register(SmallVariantQueryGestaltMatcherScores)
admin.site.register(SmallVariantQueryPediaScores)
