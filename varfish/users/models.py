from django.conf import settings
from projectroles.models import SODARUser


class User(SODARUser):
    @classmethod
    def get_kiosk_user(cls):
        """Return the Kiosk user instance."""
        user, _created = cls.objects.get_or_create(username=settings.KIOSK_USER)
        return user
