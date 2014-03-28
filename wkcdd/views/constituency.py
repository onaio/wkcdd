from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.location import LocationFactory


@view_defaults(route_name='constituency')
class ConstituencyView(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='all_communities',
                 context=LocationFactory,
                 renderer='projects_list.jinja2',
                 request_method='GET')
    def list_all_communities(self):
        pass
