from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models import Location
from wkcdd.models.constituency import Constituency
from wkcdd.models.community import Community
from wkcdd.models.project import Project
from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models.report import Report


@view_defaults(route_name='constituency')
class ConstituencyView(object):
    DEFAULT_PROJECT_TYPE = constants.DAIRY_GOAT_PROJECT_REPORT

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=Constituency,
                 renderer='constituency_communities_list.jinja2',
                 request_method='GET')
    def list_all_communities(self):
        constituency = self.request.context
        communities = Community.all(Community.parent_id == constituency.id)
        sub_county = Project.get_county(constituency)
        county = Project.get_county(sub_county)
        locations = {'sub_county': sub_county,
                     'county': county}
        impact_indicator_mapping = tuple_to_dict_list(
            ('title', 'key'), constants.IMPACT_INDICATOR_REPORT)

        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(communities,
                                                        Location.CONSTITUENCY)

        return {
            'constituency': constituency,
            'communities': communities,
            'locations': locations,
            'impact_indicators': impact_indicators,
            'impact_indicator_mapping': impact_indicator_mapping
        }

    @view_config(name='performance',
                 context=Constituency,
                 renderer='constituency_communities_performance_list.jinja2',
                 request_method='GET')
    def performance(self):
        constituency = self.request.context
        communities = Community.all(Community.parent_id == constituency.id)
        sub_county = Project.get_county(constituency)
        county = Project.get_county(sub_county)
        project_report_sectors = constants.PROJECT_REPORT_SECTORS
        locations = {'sub_county': sub_county,
                     'county': county}
        selected_project_type = (
            self.request.GET.get('type') or self.DEFAULT_PROJECT_TYPE)

        if selected_project_type not in project_report_sectors.keys():
            selected_project_type = self.DEFAULT_PROJECT_TYPE
        aggregated_indicators = (
            Report.get_performance_indicator_aggregation_for(
                communities, selected_project_type, Location.CONSTITUENCY))
        selected_project_name = project_report_sectors[selected_project_type]
        indicator_mapping = tuple_to_dict_list(
            ('title', 'group'),
            constants.PERFORMANCE_INDICATOR_REPORTS[
                selected_project_type])
        return {
            'constituency': constituency,
            'communities': communities,
            'locations': locations,
            'selected_project_type': selected_project_name,
            'project_report_sectors': project_report_sectors.items(),
            'aggregated_indicators': aggregated_indicators,
            'indicator_mapping': indicator_mapping
        }
