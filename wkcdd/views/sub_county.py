from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.constituency import Constituency
from wkcdd.models.project import Project
from wkcdd.models.report import Report
from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models import helpers


@view_defaults(route_name='sub_county')
class SubCountyView(object):
    DEFAULT_PROJECT_TYPE = constants.DAIRY_GOAT_PROJECT_REPORT

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
        county = Project.get_county(sub_county)
        locations = {'county': county}
        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(constituencies)

        return {
            'sub_county': sub_county,
            'constituencies': constituencies,
            'locations': locations,
            'impact_indicators': impact_indicators,
            'impact_indicator_mapping': tuple_to_dict_list(
                ('title', 'key'),
                constants.IMPACT_INDICATOR_REPORT)
        }

    @view_config(name='performance',
                 context=SubCounty,
                 renderer='sub_county_constituencies_performance_list.jinja2',
                 request_method='GET')
    def performance(self):
        sub_county = self.request.context
        sector_indicator_mapping = {}
        sector_aggregated_indicators = {}
        constituencies = Constituency.all(
            Constituency.parent_id == sub_county.id)
        county = Project.get_county(sub_county)
        locations = {'county': county}
        constituency_ids = [constituency.id for constituency in constituencies]
        project_types_mappings = helpers.get_project_types(
            helpers.get_community_ids(constituency_ids))
        for reg_id, report_id, title in project_types_mappings:
            aggregated_indicators = (
                Report.get_performance_indicator_aggregation_for(
                    constituencies, report_id))
            indicator_mapping = tuple_to_dict_list(
                ('title', 'group'),
                constants.PERFORMANCE_INDICATOR_REPORTS[report_id])
            sector_indicator_mapping[reg_id] = indicator_mapping
            sector_aggregated_indicators[reg_id] = aggregated_indicators

        return {
            'sub_county': sub_county,
            'constituencies': constituencies,
            'locations': locations,
            'project_types': project_types_mappings,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'sector_indicator_mapping': sector_indicator_mapping
        }
