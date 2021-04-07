import hashlib

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import ReportTemplate


class ReportTemplateForm(forms.ModelForm):
    class Meta:
        model = ReportTemplate
        fields = ("title", "filename")

    title = forms.CharField(
        label="Template Title", help_text="Leave empty to use file name", required=False
    )

    payload = forms.FileField(
        label="Template File", help_text="Upload a .docx file to use for the template."
    )

    filename = forms.CharField(
        required=False,
        help_text="Specify the file name to override the file name of the uploaded file",
        validators=[
            RegexValidator(r"(^$)|(\.docx$)", message="File name must be blank or end in .docx"),
            RegexValidator(
                r"^[a-zA-Z0-9\._-]*$",
                message="File name must only consist of alphanumeric characters, spaces, dots, hyphens, and underscores",
            ),
        ],
    )

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        if self.instance.pk:
            self.fields["payload"].required = False

    def clean(self):
        cleaned_data = self.cleaned_data
        if "payload" in cleaned_data and cleaned_data["payload"]:
            import pdb

            pdb.set_trace()
            cleaned_data["title"] = cleaned_data["title"] or cleaned_data["payload"].name
            cleaned_data["filename"] = cleaned_data["filename"] or cleaned_data["payload"].name
            ctx = hashlib.sha256()
            if cleaned_data["payload"].multiple_chunks():
                for data in cleaned_data["payload"].chunks():
                    ctx.update(data)
            else:
                ctx.update(cleaned_data["payload"].read())
            cleaned_data["filehash"] = "sha256:%s" % ctx.hexdigest()
            cleaned_data["filesize"] = cleaned_data["payload"].size

        if not cleaned_data["filename"].endswith(".docx"):
            raise ValidationError("The file name must end in .docx")

        qs = ReportTemplate.objects.filter(project=self.project, filename=cleaned_data["filename"])
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs:
            raise ValidationError(
                "There already exists a report template with file name %s in this project!"
                % cleaned_data["filename"]
            )

        return cleaned_data

    def save(self, commit=True):
        super().save(commit=False)
        if "filehash" in self.cleaned_data:
            self.instance.filehash = self.cleaned_data["filehash"]
        if "filesize" in self.cleaned_data:
            self.instance.filesize = self.cleaned_data["filesize"]
        self.instance.project = self.project
        self.instance.save()
        return self.instance
