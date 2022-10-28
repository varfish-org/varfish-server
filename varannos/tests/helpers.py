from django.conf import settings
from django.test import RequestFactory
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase
from test_plus import TestCase

from variants.tests.factories import ProjectFactory

#: A known invalid MIME type.
VARFISH_INVALID_MIMETYPE = "application/vnd.bihealth.invalid+json"
#: A known invalid version.
VARFISH_INVALID_VERSION = "0.0.0"


class TestViewsBase(TestCase):
    def setUp(self):
        super().setUp()
        self.superuser = self.make_user("superuser")
        self.superuser.is_superuser = True
        self.superuser.is_staff = True
        self.superuser.save()

        self.project = ProjectFactory()


class ViewTestBaseMixin:
    def setUp(self):
        super().setUp()
        self.request_factory = RequestFactory()


class ApiViewTestBase(ViewTestBaseMixin, TestProjectAPIPermissionBase):
    """Base class for API view testing (and file export)"""

    media_type = settings.SODAR_API_MEDIA_TYPE
    api_version = settings.SODAR_API_DEFAULT_VERSION

    def setUp(self):
        super().setUp()

        self.knox_token = self.get_token(self.superuser)
