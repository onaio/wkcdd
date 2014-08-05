from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pyramid.security import (
    remember, forget)
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from wkcdd.models.user import User
from wkcdd.views.helpers import check_post_csrf


@view_config(route_name='auth',
             match_param='action=login',
             renderer='sign_in.jinja2',
             decorator=check_post_csrf)
@view_config(name='login',
             context=HTTPForbidden,
             renderer='sign_in.jinja2')
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.get(User.username == username)
        except NoResultFound:
            # we're still here set the error message
            request.session.flash(u"Invalid username or password", 'error')
        else:
            if user.active is False:
                # we're still here set the error message
                request.session.flash(
                    u"Inactive account, please contact your supervisor",
                    'error')
            elif user.check_password(password):
                headers = remember(request, user.id)
                return HTTPFound(
                    request.route_url(
                        'reports', traverse=()), headers=headers)
            else:
                # we're still here set the error message
                request.session.flash(u"Invalid username or password", 'error')
    return {}


@view_config(route_name='auth', match_param='action=logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(
        request.route_url(
            'performance_indicators', traverse=()), headers=headers)
