from test_plus.test import TestCase


class TestUser(TestCase):
    def setUp(self):
        self.superuser = self.make_user()

    def test__str__(self):
        self.assertEqual(
            self.superuser.__str__(),
            "testuser",  # This is the default username for self.make_user()
        )
