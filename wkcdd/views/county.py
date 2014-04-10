from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models.location import LocationFactory
from wkcdd.models.location import Location
from wkcdd.models.county import County
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.report import Report
from wkcdd.views.helpers import build_dataset


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
        return {
            'title': "County Impact Indicators Report",
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
        }

    @view_config(name='',
                 context=County,
                 renderer='county_sub_counties_list.jinja2',
                 request_method='GET')
    def list_all_sub_counties(self):
        county = self.request.context
        sub_counties = SubCounty.all(SubCounty.parent_id == county.id)

        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(
                sub_counties, Location.COUNTY)
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
        sub_counties = SubCounty.all(SubCounty.parent_id == county.id)
        selected_project_type = (
            self.request.GET.get('type') or self.DEFAULT_PROJECT_TYPE)
        project_report_sectors = constants.PROJECT_REPORT_SECTORS
        if selected_project_type not in project_report_sectors.keys():
            selected_project_type = self.DEFAULT_PROJECT_TYPE
        aggregated_indicators = (
            Report.get_performance_indicator_aggregation_for(
                sub_counties, selected_project_type, Location.COUNTY))
        selected_project_name = project_report_sectors[selected_project_type]
        indicator_mapping = tuple_to_dict_list(
            ('title', 'group'),
            constants.PERFORMANCE_INDICATOR_REPORTS[
                selected_project_type])
        return {
            'county': county,
            'sub_counties': sub_counties,
            'selected_project_type': selected_project_name,
            'project_report_sectors': project_report_sectors.items(),
            'aggregated_indicators': aggregated_indicators,
            'indicator_mapping': indicator_mapping
        }
