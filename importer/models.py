from django.db import models


class ImportInfo(models.Model):
    table = models.CharField(max_length=16)
    timestamp = models.DateTimeField(editable=False)
    release = models.CharField(max_length=16)
    comment = models.CharField(max_length=1024)
