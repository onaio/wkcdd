from pyramid.security import authenticated_userid
from pyramid.response import Response
from pyramid.view import (
    view_config,
    forbidden_view_config,
    render_view
)
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPFound
)


@forbidden_view_config()
def forbidden(context, request):
    user_id = authenticated_userid(request)
    # if user is NOT authenticated, raise HTTPUnauthorized
    if not user_id:
        return Response(
            render_view(
                context, request, 'login', secure=False), status=401)
    # otherwise, raise HTTPForbidden
    return HTTPForbidden()


@view_config(route_name='auth',
             match_param='action=login')
@view_config(name='login',
             context=HTTPForbidden,
             renderer='login.jinja2')
def login(request):
    return Response('Login to proceed')


@view_config(route_name='default')
def home(request):
    return HTTPFound(request.route_url('county', traverse=()))


@view_config(route_name='private', permission="authenticated")
def private(request):
    return Response("Private view")


@view_config(route_name='supervisors_only', permission="supervise")
def very_private(request):
    return Response("Very Private view")


@view_config(route_name='reporting_status', renderer='reporting_status.jinja2')
def under_construction(request):
    return {}
