from pyramid.view import (
    view_config,
    view_defaults,
)


@view_defaults(route_name='projects')
class ProjectViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='projects',
                 renderer='projects.jinja2')
    def list_projects(self):

        return {}
