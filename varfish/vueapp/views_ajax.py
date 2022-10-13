from projectroles.app_settings import AppSettingAPI
from rest_framework import status, views
from rest_framework.exceptions import APIException
from rest_framework.response import Response

app_settings = AppSettingAPI()

SETTING_INLINE_HELP = "vueapp.filtration_inline_help"

SETTING_COMPLEXITY_MODE = "vueapp.filtration_complexity_mode"

ALLOWED_SETTING_NAMES = (SETTING_INLINE_HELP, SETTING_COMPLEXITY_MODE)


class UserSettingView(views.APIView):
    """Helper view

    Eventually, sodar-core will implement this in projectroles and this can go away.
    """

    def _check_setting(self, is_post=False):
        if self.kwargs.get("setting_name") not in ALLOWED_SETTING_NAMES:
            raise APIException(
                detail="Invalid setting name",
                code=500,
            )
        if not is_post:
            return
        if self.kwargs["setting_name"] == SETTING_INLINE_HELP:
            if self.request.data.get("value") not in [True, False]:
                raise APIException(
                    detail="'value' must be true/false",
                    code=500,
                )
        elif self.kwargs["setting_name"] == SETTING_COMPLEXITY_MODE:
            if self.request.data.get("value") not in ["simple", "normal", "advanced", "dev"]:
                raise APIException(
                    detail="'value' must be simple/normal/advanced",
                    code=500,
                )

    def get(self, request, *args, **kwargs):
        self._check_setting()
        value = app_settings.get_app_setting(
            *self.kwargs["setting_name"].split("."), user=self.request.user
        )
        return Response({"value": value}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        self._check_setting(is_post=True)
        app_settings.set_app_setting(
            *self.kwargs["setting_name"].split("."),
            self.request.data["value"],
            user=self.request.user
        )
        return self.get(request, *args, **kwargs)
