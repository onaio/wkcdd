from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models import Location
from wkcdd.models.constituency import Constituency
from wkcdd.models.community import Community
from wkcdd.models.report import Report
from wkcdd.models import helpers
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
        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(communities)
        dataset = build_dataset(Location.COMMUNITY,
                                communities,
                                impact_indicators)
        return {
            'title': constituency.pretty,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'constituency': constituency
        }

    @view_config(name='performance',
                 context=Constituency,
                 renderer='constituency_communities_performance_list.jinja2',
                 request_method='GET')
    def performance(self):
        constituency = self.request.context
        communities = Community.all(Community.parent_id == constituency.id)
        community_ids = [community.id for community in communities]
        project_types_mappings = helpers.get_project_types(community_ids)
        sector_indicator_mapping = {}
        sector_aggregated_indicators = {}
        for reg_id, report_id, title in project_types_mappings:
            aggregated_indicators = (
                Report.get_performance_indicator_aggregation_for(
                    communities, report_id))
            indicator_mapping = tuple_to_dict_list(
                ('title', 'group'),
                constants.PERFORMANCE_INDICATOR_REPORTS[report_id])
            sector_indicator_mapping[reg_id] = indicator_mapping
            sector_aggregated_indicators[reg_id] = aggregated_indicators
        return {
            'title': constituency.pretty,
            'constituency': constituency,
            'communities': communities,
            'project_types': project_types_mappings,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'sector_indicator_mapping': sector_indicator_mapping
        }
