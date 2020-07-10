from django import forms
from projectroles.app_settings import AppSettingAPI
from cohorts.models import Cohort
from variants.models import Case

app_settings = AppSettingAPI()


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
        self.fields["cases"] = forms.ModelMultipleChoiceField(
            # Turn the cases many-to-many relation into a checkbox field
            widget=forms.CheckboxSelectMultiple,
            # Limit the choices to what the user is allowed to see
            queryset=cases,
        )

    class Meta:
        model = Cohort
        #: ``project`` and ``user`` field are filled automatically
        fields = ("name", "cases")
