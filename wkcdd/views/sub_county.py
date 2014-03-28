from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.location import LocationFactory


@view_defaults(route_name='sub_county')
class SubCountyView(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='all_constituencies',
                 context=LocationFactory,
                 renderer='projects_list.jinja2',
                 request_method='GET')
    def list_all_constituencies(self):
        pass
