from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models.location import (
    LocationFactory,
    Location
)
from wkcdd.models.county import County
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.project import Project
from wkcdd.models.report import Report
from wkcdd.models import helpers
from wkcdd.views.helpers import (
    build_dataset,
    generate_impact_indicators_for
)


@view_defaults(route_name='counties')
class CountyView(object):
    DEFAULT_PROJECT_TYPE = constants.DAIRY_GOAT_PROJECT_REPORT

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
        view_by = self.request.GET.get('view_by')
        location_map = self.get_location_map()

        impact_indicator_results = generate_impact_indicators_for(location_map)
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
        search_criteria = {'view_by': view_by,
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
        sector_indicator_mapping = {}
        sector_aggregated_indicators = {}
        location_map = self.get_location_map()
        view_by = self.request.GET.get('view_by')

        county = self.request.context
        sub_counties = SubCounty.all(SubCounty.parent_id == county.id)
        sub_county_ids = [subcounty.id for subcounty in sub_counties]
        project_types_mappings = helpers.get_project_types(
            helpers.get_community_ids(
                helpers.get_constituency_ids(
                    sub_county_ids)))
        for reg_id, report_id, title in project_types_mappings:
            aggregated_indicators = (
                Report.get_performance_indicator_aggregation_for(
                    sub_counties, report_id))
            indicator_mapping = tuple_to_dict_list(
                ('title', 'group'),
                constants.PERFORMANCE_INDICATOR_REPORTS[report_id])
            sector_indicator_mapping[reg_id] = indicator_mapping
            sector_aggregated_indicators[reg_id] = aggregated_indicators
        filter_criteria = Project.generate_filter_criteria()

        search_criteria = {'view_by': view_by,
                           'location_map': location_map}
        return {
            'title': county.pretty,
            'county': county,
            'sub_counties': sub_counties,
            'project_types': project_types_mappings,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'sector_indicator_mapping': sector_indicator_mapping,
            'filter_criteria': filter_criteria,
            'search_criteria': search_criteria
        }

    @view_config(name='performance_summary',
                 context=LocationFactory,
                 renderer='counties_performance_list.jinja2',
                 request_method='GET')
    def performance_summary(self):
        sector_indicator_mapping = {}
        sector_aggregated_indicators = {}
        counties = County.all()
        county_ids = [county.id for county in counties]

        location_map = self.get_location_map()
        view_by = self.request.GET.get('view_by')
        search_criteria = {'view_by': view_by,
                           'location_map': location_map}

        project_types_mappings = helpers.get_project_types(
            helpers.get_community_ids(
                helpers.get_constituency_ids(
                    helpers.get_sub_county_ids(
                        county_ids))))
        for reg_id, report_id, title in project_types_mappings:
            aggregated_indicators = (
                Report.get_performance_indicator_aggregation_for(
                    counties, report_id))
            indicator_mapping = tuple_to_dict_list(
                ('title', 'group'),
                constants.PERFORMANCE_INDICATOR_REPORTS[report_id])
            sector_indicator_mapping[reg_id] = indicator_mapping
            sector_aggregated_indicators[reg_id] = aggregated_indicators
        filter_criteria = Project.generate_filter_criteria()
        return {
            'title': "County Performance Indicators Report",
            'counties': counties,
            'project_types': project_types_mappings,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'sector_indicator_mapping': sector_indicator_mapping,
            'filter_criteria': filter_criteria,
            'search_criteria': search_criteria
        }
