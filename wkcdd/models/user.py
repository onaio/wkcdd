from pyramid.security import Allow
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean
)

from sqlalchemy.orm import synonym
from sqlalchemy.orm.exc import NoResultFound
from wkcdd.models.base import Base, BaseModelFactory, DBSession

ADMIN_PERM = 'admin'
CPC_PERM = 'cpc'

GROUPS = {
    ADMIN_PERM: ['g:admin'],
    CPC_PERM: ['g:user']}


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    pwd = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=False, server_default='false')
    group = Column(String(10), nullable=False, server_default=CPC_PERM)

    @property
    def password(self):
        return self.pwd

    @password.setter
    def password(self, value):
        from wkcdd.security import pwd_context
        self.pwd = pwd_context.encrypt(value)

    password = synonym('pwd', descriptor=password)

    def check_password(self, password):
        from wkcdd.security import pwd_context
        # always return false if password is greater than 255 to avoid
        # spoofing attacks
        if len(password) > 255:
            return False
        return pwd_context.verify(password, self.pwd)

    @property
    def appstruct(self):
        return {
            'username': self.username,
            'active': self.active,
            'group': self.group
        }

    def update(self, username, pwd, active, group):
        self.username = username
        self.password = pwd
        self.active = active
        self.group = group
        self.save()


class UserFactory(BaseModelFactory):
    __acl__ = [
        (Allow, ADMIN_PERM, 'manage')
    ]

    def __getitem__(self, item):
        # try to retrieve the user whose id matches item
        try:
            user_id = int(item)
            user = DBSession.query(User).filter_by(id=user_id).one()
        except (ValueError, NoResultFound):
            raise KeyError
        else:
            user.__parent__ = self
            user.__name__ = item
            return user
