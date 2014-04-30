from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd.models import Location
from wkcdd.models.constituency import Constituency
from wkcdd.models.community import Community
from wkcdd.models.report import Report
from wkcdd.views.helpers import (
    build_dataset,
    generate_performance_indicators_for
)


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
        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(communities)
        dataset = build_dataset(Location.COMMUNITY,
                                communities,
                                impact_indicators)
        search_criteria = {'view_by': 'communities'}

        return {
            'title': constituency.pretty,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'constituency': constituency,
            'search_criteria': search_criteria
        }

    @view_config(name='performance',
                 context=Constituency,
                 renderer='constituency_communities_performance_list.jinja2',
                 request_method='GET')
    def performance(self):
        constituency = self.request.context
        location_map = {
            'community': '',
            'constituency': constituency.id,
            'sub_county': '',
            'county': ''
        }
        default_level = 'communities'
        level = self.request.GET.get('view_by') or default_level
        selected_project_type = self.request.GET.get('type')
        search_criteria = {'view_by': level,
                           'location_map': location_map}
        indicators = generate_performance_indicators_for(
            location_map, selected_project_type, level)
        project_types = indicators['project_types']
        aggregate_type = indicators['aggregate_type']
        sector_aggregated_indicators = (
            indicators['sector_aggregated_indicators'])
        return {
            'title': constituency.pretty,
            'aggregate_type': aggregate_type,
            'constituency': constituency,
            'project_types': project_types,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'search_criteria': search_criteria
        }
