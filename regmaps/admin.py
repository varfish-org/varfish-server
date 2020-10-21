from django.contrib import admin

from .models import (
    RegMapCollection,
    RegMap,
    RegElementType,
    RegElement,
    RegInteraction,
)

# Register your models here.
admin.site.register((RegMapCollection, RegMap, RegElementType, RegElement, RegInteraction,))
