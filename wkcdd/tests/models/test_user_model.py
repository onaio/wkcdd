from wkcdd.models.user import User, CPC_PERM
from wkcdd.tests.test_base import IntegrationTestBase


class TestUser(IntegrationTestBase):
    def test_user_update(self):
        self._create_user(username='test_user', password="123456")
        user = User.get(User.username == 'test_user')

        self.assertNotEqual(user.pwd, "123456")

        user.update("another_test_user",
                    "password",
                    True,
                    CPC_PERM)

        self.assertNotEqual(user.pwd, "password")
