from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd import constants
from wkcdd.models.location import (
    LocationFactory,
    Location
)
from wkcdd.models.county import County
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.project import Project
from wkcdd.models.report import Report
from wkcdd.views.helpers import (
    build_dataset,
    generate_impact_indicators_for,
    generate_performance_indicators_for
)


@view_defaults(route_name='counties')
class CountyView(object):
    DEFAULT_PROJECT_TYPE = constants.DAIRY_GOAT_PROJECT_REGISTRATION
    DEFAULT_LEVEL = 'counties'

    def __init__(self, request):
        self.request = request

    def get_location_map(self):
        location_map = {
            'community': self.request.GET.get('community'),
            'constituency': self.request.GET.get('constituency'),
            'sub_county': self.request.GET.get('sub_county'),
            'county': self.request.GET.get('county')
        }
        return location_map

    @view_config(name='',
                 context=LocationFactory,
                 renderer='counties_list.jinja2',
                 request_method='GET')
    def show_all(self):
        filter_criteria = Project.generate_filter_criteria()
        level = self.request.GET.get('view_by') or self.DEFAULT_LEVEL
        location_map = self.get_location_map()

        impact_indicator_results = \
            generate_impact_indicators_for(location_map, level)
        aggregate_type = impact_indicator_results['aggregate_type']
        location = impact_indicator_results['location']

        if aggregate_type is 'Project':
            dataset = build_dataset(
                aggregate_type,
                None,
                impact_indicator_results['impact_indicators'],
                impact_indicator_results['aggregate_list'])
        else:
            dataset = build_dataset(
                aggregate_type,
                impact_indicator_results['aggregate_list'],
                impact_indicator_results['impact_indicators'])

        search_criteria = {'view_by': level,
                           'location_map': location_map}
        return {
            'title': "Impact Indicators Report",
            'location': location,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'filter_criteria': filter_criteria,
            'search_criteria': search_criteria
        }

    @view_config(name='',
                 context=County,
                 renderer='county_sub_counties_list.jinja2',
                 request_method='GET')
    def list_all_sub_counties(self):
        county = self.request.context
        sub_counties = SubCounty.all(SubCounty.parent_id == county.id)

        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(sub_counties)
        dataset = build_dataset(Location.SUB_COUNTY,
                                sub_counties,
                                impact_indicators)
        return {
            'title': county.pretty,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'county': county
        }

    @view_config(name='performance',
                 context=County,
                 renderer='county_sub_counties_performance_list.jinja2',
                 request_method='GET')
    def performance(self):
        county = self.request.context
        location_map = {
            'community': '',
            'constituency': '',
            'sub_county': '',
            'county': county.id
        }
        level = self.request.GET.get('view_by') or self.DEFAULT_LEVEL

        search_criteria = {'view_by': level,
                           'location_map': location_map}
        indicators = generate_performance_indicators_for(
            location_map)
        project_types = indicators['project_types']
        aggregate_type = indicators['aggregate_type']
        sector_aggregated_indicators = (
            indicators['sector_aggregated_indicators'])

        filter_criteria = Project.generate_filter_criteria()

        return {
            'title': county.pretty,
            'aggregate_type': aggregate_type,
            'county': county,
            'project_types': project_types,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'filter_criteria': filter_criteria,
            'search_criteria': search_criteria
        }

    @view_config(name='performance_summary',
                 context=LocationFactory,
                 renderer='counties_performance_list.jinja2',
                 request_method='GET')
    def performance_summary(self):
        location_map = self.get_location_map()
        level = self.request.GET.get('view_by') or self.DEFAULT_LEVEL

        selected_project_type = self.request.GET.get('type')
        if selected_project_type == 'default':
            selected_project_type = ''
        elif selected_project_type == '':
            selected_project_type = self.DEFAULT_PROJECT_TYPE

        search_criteria = {'view_by': level,
                           'location_map': location_map}
        indicators = generate_performance_indicators_for(
            location_map,
            selected_project_type,
            level)

        location = indicators['location']
        project_types = indicators['project_types']
        aggregate_type = indicators['aggregate_type']
        sector_aggregated_indicators = (
            indicators['sector_aggregated_indicators'])
        project_type_geopoints = indicators['project_type_geopoints']

        sector_indicator_mapping = indicators['sector_indicator_mapping']
        filter_criteria = Project.generate_filter_criteria()

        selected_project_label = [label
                                  for sector, report, label in project_types
                                  if sector == selected_project_type]
        selected_project_label = (selected_project_label[0]
                                  if selected_project_label else '')

        return {
            'title': "Performance Indicators Report",
            'aggregate_type': aggregate_type,
            'location': location,
            'project_types': project_types,
            'selected_project_type': selected_project_type,
            'selected_project_label': selected_project_label,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'sector_indicator_mapping': sector_indicator_mapping,
            'filter_criteria': filter_criteria,
            'search_criteria': search_criteria,
            'project_type_geopoints': project_type_geopoints
        }
