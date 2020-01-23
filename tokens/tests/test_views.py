from test_plus.test import TestCase

from django.urls import reverse
from knox.models import AuthToken


class UserTokenListViewTest(TestCase):
    """Test the ``UserTokenListView``"""

    def setUp(self):
        self.user = self.make_user()

    def make_token(self):
        self.tokens = [AuthToken.objects.create(self.user, None)]

    def testListEmpty(self):
        """Test that rendering the list view without any tokens works"""
        with self.login(self.user):
            response = self.get("tokens:token-list")
        self.response_200(response)
        self.assertEqual(len(response.context["object_list"]), 0)

    def testListOne(self):
        """Test that rendering the list view with one token works"""
        self.make_token()
        with self.login(self.user):
            response = self.get("tokens:token-list")
        self.response_200(response)
        self.assertEqual(len(response.context["object_list"]), 1)


class UserTokenCreateViewTest(TestCase):
    """Test the ``UserTokenCreateView``"""

    def setUp(self):
        self.user = self.make_user()

    def testGet(self):
        """Test that showing the creation form works"""
        with self.login(self.user):
            response = self.get("tokens:token-create")
        self.response_200(response)
        self.assertIsNotNone(response.context["form"])

    def testPostSuccessNoTtl(self):
        """Test creating an authentication token with TTL=0 works"""
        self.assertEqual(AuthToken.objects.count(), 0)
        with self.login(self.user):
            response = self.post("tokens:token-create", data={"ttl": 0})
        self.response_200(response)
        self.assertEqual(AuthToken.objects.count(), 1)

    def testPostSuccessWithTtl(self):
        """Test creating an authentication token with TTL != 0 works"""
        self.assertEqual(AuthToken.objects.count(), 0)
        with self.login(self.user):
            response = self.post("tokens:token-create", data={"ttl": 10})
        self.response_200(response)
        self.assertEqual(AuthToken.objects.count(), 1)


class UserTokenDeleteViewTest(TestCase):
    """Test the ``UserTokenDeleteView``"""

    def setUp(self):
        self.user = self.make_user()
        AuthToken.objects.create(user=self.user)
        self.token = AuthToken.objects.first()

    def testGet(self):
        """Test that showing the deletion form works"""
        with self.login(self.user):
            response = self.get("tokens:token-delete", pk=self.token.pk)
        self.response_200(response)

    def testPostSuccess(self):
        """Test that deleting a token works"""
        self.assertEqual(AuthToken.objects.count(), 1)
        with self.login(self.user):
            response = self.post("tokens:token-delete", pk=self.token.pk)
        self.response_302(response)
        self.assertRedirects(response, reverse("tokens:token-list"), fetch_redirect_response=False)
