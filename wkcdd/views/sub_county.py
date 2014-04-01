from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.constituency import Constituency
from wkcdd.models.project import Project
from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list


@view_defaults(route_name='sub_county')
class SubCountyView(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=SubCounty,
                 renderer='sub_county_constituencies_list.jinja2',
                 request_method='GET')
    def list_all_constituencies(self):
        sub_county = self.request.context
        constituencies = Constituency.all(
            Constituency.parent_id == sub_county.id)
        county = Project.get_county(sub_county)
        locations = {'county': county}
        return {
            'sub_county': sub_county,
            'constituencies': constituencies,
            'locations': locations,
            'impact_indicator_mapping': tuple_to_dict_list(
                ('title', 'key'),
                constants.IMPACT_INDICATOR_REPORT)
        }
