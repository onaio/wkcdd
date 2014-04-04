from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models import Location
from wkcdd.models.constituency import Constituency
from wkcdd.models.community import Community
from wkcdd.models.project import Project
from wkcdd import constants
from wkcdd.models.report import Report
from wkcdd.views.helpers import build_dataset


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
        impact_indicators = \
            Report.get_location_indicator_aggregation(communities,
                                                      Location.CONSTITUENCY)
        dataset = build_dataset(Location.CONSTITUENCY,
                                communities,
                                constants,
                                impact_indicators)

        return {
            'title': constituency.name,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'locations': locations
        }
