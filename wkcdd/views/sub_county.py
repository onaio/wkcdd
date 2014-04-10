from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models.location import Location
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.constituency import Constituency
from wkcdd.models.project import Project
from wkcdd.models.report import Report
from wkcdd.views.helpers import build_dataset


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
        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(
                constituencies, Location.SUB_COUNTY)
        dataset = build_dataset(Location.CONSTITUENCY,
                                constituencies,
                                impact_indicators)
        return {
            'title': sub_county.pretty,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'sub_county': sub_county
        }

    @view_config(name='performance',
                 context=SubCounty,
                 renderer='sub_county_constituencies_performance_list.jinja2',
                 request_method='GET')
    def performance(self):
        sub_county = self.request.context
        constituencies = Constituency.all(
            Constituency.parent_id == sub_county.id)
        county = Project.get_county(sub_county)
        locations = {'county': county}
        project_report_sectors = constants.PROJECT_REPORT_SECTORS
        selected_project_type = (
            self.request.GET.get('type') or self.DEFAULT_PROJECT_TYPE)

        if selected_project_type not in project_report_sectors.keys():
            selected_project_type = self.DEFAULT_PROJECT_TYPE
        aggregated_indicators = (
            Report.get_performance_indicator_aggregation_for(
                constituencies, selected_project_type, Location.SUB_COUNTY))
        selected_project_name = project_report_sectors[selected_project_type]
        indicator_mapping = tuple_to_dict_list(
            ('title', 'group'),
            constants.PERFORMANCE_INDICATOR_REPORTS[
                selected_project_type])
        return {
            'sub_county': sub_county,
            'constituencies': constituencies,
            'locations': locations,
            'selected_project_type': selected_project_name,
            'project_report_sectors': project_report_sectors.items(),
            'aggregated_indicators': aggregated_indicators,
            'indicator_mapping': indicator_mapping
        }
