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
    get_project_geolocations
)

@view_defaults(route_name='counties')
class CountyView(object):
    DEFAULT_PROJECT_TYPE = constants.DAIRY_GOAT_PROJECT_REPORT

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=LocationFactory,
                 renderer='counties_list.jinja2',
                 request_method='GET')
    def show_all_counties(self):
        counties = County.all()
        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(counties)
        dataset = build_dataset(Location.COUNTY,
                                counties,
                                impact_indicators)
        filter_criteria = Project.generate_filter_criteria()
        return {
            'title': "County Impact Indicators Report",
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'filter_criteria': filter_criteria
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
        return {
            'title': county.pretty,
            'county': county,
            'sub_counties': sub_counties,
            'project_types': project_types_mappings,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'sector_indicator_mapping': sector_indicator_mapping,
            'filter_criteria': filter_criteria
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
        project_types_mappings = helpers.get_project_types(
            helpers.get_community_ids(
                helpers.get_constituency_ids(
                    helpers.get_sub_county_ids(
                        county_ids))))

        project_type = self.request.GET.get('type')

        if project_type:
            selected_project_types = helpers.get_project_types(
                helpers.get_community_ids(
                    helpers.get_constituency_ids(
                        helpers.get_sub_county_ids(
                            county_ids))), Project.sector == project_type)

        else:
            selected_project_types = project_types_mappings
        project_type_geopoints = {}
        for reg_id, report_id, title in project_types_mappings:
            aggregated_indicators = (
                Report.get_performance_indicator_aggregation_for(
                    counties, report_id))
            indicator_mapping = tuple_to_dict_list(
                ('title', 'group'),
                constants.PERFORMANCE_INDICATOR_REPORTS[report_id])
            sector_indicator_mapping[reg_id] = indicator_mapping
            sector_aggregated_indicators[reg_id] = aggregated_indicators
            project_geopoints = get_project_geolocations(aggregated_indicators['project_list'])
            project_type_geopoints[reg_id] = project_geopoints

        filter_criteria = Project.generate_filter_criteria()

        return {
            'title': "County Performance Indicators Report",
            'counties': counties,
            'project_types': project_types_mappings,
            'selected_project_types': selected_project_types,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'sector_indicator_mapping': sector_indicator_mapping,
            'filter_criteria': filter_criteria,
            'project_type_geopoints': project_type_geopoints

        }
