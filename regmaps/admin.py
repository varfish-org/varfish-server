from django.contrib import admin

from .models import RegElement, RegElementType, RegInteraction, RegMap, RegMapCollection

# Register your models here.
admin.site.register(
    (
        RegMapCollection,
        RegMap,
        RegElementType,
        RegElement,
        RegInteraction,
    )
)
