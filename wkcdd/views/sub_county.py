from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd.models.sub_county import SubCounty
from wkcdd.models.location import Location
from wkcdd.models.constituency import Constituency
from wkcdd.models.report import Report
from wkcdd.views.helpers import (
    build_dataset,
    generate_performance_indicators_for
)


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
        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(constituencies)
        dataset = build_dataset(Location.CONSTITUENCY,
                                constituencies,
                                impact_indicators)
        search_criteria = {'view_by': 'constituencies'}
        return {
            'title': sub_county.pretty,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'sub_county': sub_county,
            'search_criteria': search_criteria
        }

    @view_config(name='performance',
                 context=SubCounty,
                 renderer='sub_county_constituencies_performance_list.jinja2',
                 request_method='GET')
    def performance(self):
        sub_county = self.request.context
        location_map = {
            'community': '',
            'constituency': '',
            'sub_county': sub_county.id,
            'county': ''
        }
        default_level = 'constituencies'
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
            'title': sub_county.pretty,
            'aggregate_type': aggregate_type,
            'sub_county': sub_county,
            'project_types': project_types,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'search_criteria': search_criteria
        }
