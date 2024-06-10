from django.contrib import admin

from .models import (
    AssertionMethod,
    Family,
    Individual,
    Organisation,
    Submission,
    SubmissionIndividual,
    SubmissionSet,
    Submitter,
    SubmittingOrg,
)

# Register your models here.

admin.site.register(Family)
admin.site.register(Individual)
admin.site.register(SubmissionIndividual)
admin.site.register(AssertionMethod)
admin.site.register(Submitter)
admin.site.register(Organisation)
admin.site.register(SubmissionSet)
admin.site.register(Submission)
admin.site.register(SubmittingOrg)
