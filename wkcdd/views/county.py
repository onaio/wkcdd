from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.location import LocationFactory
from wkcdd.models.county import County
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.report import Report
from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models import helpers


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

        return{
            'counties': counties,
            'impact_indicators': impact_indicators,
            'impact_indicator_mapping': tuple_to_dict_list(
                ('title', 'key'),
                constants.IMPACT_INDICATOR_REPORT)
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

        return {
            'county': county,
            'sub_counties': sub_counties,
            'impact_indicators': impact_indicators,
            'impact_indicator_mapping': tuple_to_dict_list(
                ('title', 'key'),
                constants.IMPACT_INDICATOR_REPORT)
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
        return {
            'county': county,
            'sub_counties': sub_counties,
            'project_types': project_types_mappings,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'sector_indicator_mapping': sector_indicator_mapping
        }
