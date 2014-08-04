from pyramid.view import view_config, view_defaults

from wkcdd.models.user import User, UserFactory
from wkcdd.views.base import BaseClassViews
from wkcdd.views.helpers import check_post_csrf


@view_defaults(route_name='users', permission="authenticated")
class AdminView(BaseClassViews):

    @view_config(name='',
                 context=UserFactory,
                 renderer='admin_users_list.jinja2',
                 request_method='GET')
    def list(self):
        # display list of registered users for administration
        users = User.all()
        return {'users': users}

    @view_config(name='add',
                 context=UserFactory,
                 renderer='add_users.jinja2',
                 decorator=check_post_csrf)
    def add_user(self):
        # validate form submission
        # add user
        # redirect to user admin view
        pass

    @view_config(name='edit',
                 context=UserFactory,
                 renderer='add_users.jinja2',
                 decorator=check_post_csrf)
    def edit(self):
        # update user to be either admin or inactive
        pass
