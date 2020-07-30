from django import forms
from django.forms import ModelMultipleChoiceField, MultipleChoiceField
from django.forms.models import ModelChoiceIterator
from projectroles.app_settings import AppSettingAPI
from cohorts.models import Cohort
from variants.models import Case

app_settings = AppSettingAPI()


class CustomModelChoiceIterator(ModelChoiceIterator):
    def choice(self, obj):
        return (
            self.field.prepare_value(obj),
            self.field.label_from_instance(obj),
            obj,
        )


class CustomModelMultipleChoiceField(ModelMultipleChoiceField):
    def _get_choices(self):
        if hasattr(self, "_choices"):
            return self._choices
        return CustomModelChoiceIterator(self)

    choices = property(_get_choices, ModelMultipleChoiceField._set_choices)


class CohortForm(forms.ModelForm):
    """Form for creating and updating cohorts.

    Requires a user object as the user's role will influence the choices of the form.
    """

    def __init__(self, *args, **kwargs):
        # User of the form
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        if user.is_superuser:
            cases = Case.objects.all()
        else:
            cases = Case.objects.filter(project__roles__user=user)
        # Alter the cases field
        self.fields["cases"] = CustomModelMultipleChoiceField(
            # Turn the cases many-to-many relation into a checkbox field
            widget=forms.CheckboxSelectMultiple,
            # Limit the choices to what the user is allowed to see
            queryset=cases.order_by("name"),
        )

    class Meta:
        model = Cohort
        #: ``project`` and ``user`` field are filled automatically
        fields = ("name", "cases")
