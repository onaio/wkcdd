from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models import Location
from wkcdd.models.constituency import Constituency
from wkcdd.models.community import Community
from wkcdd.models.project import Project
from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models.report import Report


@view_defaults(route_name='constituency')
class ConstituencyView(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=Constituency,
                 renderer='constituency_communities_list.jinja2',
                 request_method='GET')
    def list_all_communities(self):
        constituency = self.request.context
        communities = Community.all(Community.parent_id == constituency.id)
        sub_county = Project.get_county(constituency)
        county = Project.get_county(sub_county)
        locations = {'sub_county': sub_county,
                     'county': county}
        impact_indicator_mapping = tuple_to_dict_list(
            ('title', 'key'), constants.IMPACT_INDICATOR_REPORT)

        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(communities,
                                                        Location.CONSTITUENCY)

        return {
            'constituency': constituency,
            'communities': communities,
            'locations': locations,
            'impact_indicators': impact_indicators,
            'impact_indicator_mapping': impact_indicator_mapping
        }
