# import uuid as uuid_object

# from django.db import models


# class CaseImportAction(models.Model):
#     """Stores the necessary information for importing a case."""

#     #: Record UUID.
#     sodar_uuid = models.UUIDField(
#         default=uuid_object.uuid4, unique=True
#     )
#     #: DateTime of creation.
#     date_created = models.DateTimeField(auto_now_add=True)
#     #: DateTime of last modification.
#     date_modified = models.DateTimeField(auto_now=True)

#     project = models.ForeignKey(
#         Project, on_delete=models.CASCADE, help_text="Project that is imported to"
#     )

#     class Meta:
#         #: Order by date of last modification (most recent first).
#         ordering = ("-date_modified",)
