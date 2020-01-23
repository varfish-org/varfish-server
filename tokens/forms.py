from django import forms


class UserTokenCreateForm(forms.Form):
    """This form allows token creation"""

    #: Time to live in hours
    ttl = forms.IntegerField(
        label="Time to live",
        min_value=0,
        required=True,
        initial=0,
        help_text="Time to live in hours, set to 0 for tokens that never expire.",
    )
