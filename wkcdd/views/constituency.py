from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.constituency import Constituency


@view_defaults(route_name='constituency')
class ConstituencyView(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=Constituency,
                 renderer='projects_list.jinja2',
                 request_method='GET')
    def list_all_communities(self):
        constituency = self.request.context
        return {
            'constituency': constituency
        }
