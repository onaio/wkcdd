from passlib.context import CryptContext
from sqlalchemy.orm.exc import NoResultFound
from wkcdd.models.user import GROUPS
from wkcdd.models.user import User

pwd_context = CryptContext()

ADMIN_PERM = "admin"


def group_finder(userid, request):
    try:
        user = User.get(User.id == userid)
    except NoResultFound:
        return None
    else:
        return GROUPS.get(user.group, [])
