from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.community import Community
from wkcdd.models.project import Project
from wkcdd.models.report import Report
from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models import utils


@view_defaults(route_name='community')
class CommunityView(object):
    DEFAULT_PROJECT_TYPE = constants.DAIRY_GOAT_PROJECT_REPORT

    def __init__(self, request):
        self.request = request

    @view_config(name='show',
                 context=Community,
                 renderer='community_projects_list.jinja2',
                 request_method='GET')
    def show(self):
        community = self.request.context
        projects = utils.get_project_list([community.id])
        locations = self.get_locations(community)
        indicator_mapping, aggregated_indicators = (
            self.get_impact_indicators(projects))
        return {
            'community': community,
            'locations': locations,
            'aggregated_indicators': aggregated_indicators,
            'indicator_mapping': indicator_mapping
        }

    @view_config(name='performance',
                 context=Community,
                 renderer='community_projects_performance_table.jinja2',
                 request_method='GET')
    def performance(self):
        community = self.request.context
        projects = community.projects
        locations = self.get_locations(community)
        indicator_mapping, aggregated_indicators = (
            self.get_performance_indicators(projects))
        return {
            'community': community,
            'locations': locations,
            'project_types': constants.PROJECT_REPORT_SECTORS.values(),
            'aggregated_indicators': aggregated_indicators,
            'indicator_mapping': indicator_mapping
        }

    def get_locations(self, community):
        constituency = Project.get_constituency(community)
        sub_county = Project.get_county(constituency)
        county = Project.get_county(sub_county)
        locations = {'constituency': constituency,
                     'sub_county': sub_county,
                     'county': county}
        return locations

    def get_impact_indicators(self, projects):
        aggregated_indicators = (
            Report.get_aggregated_project_indicators(projects))
        indicator_mapping = tuple_to_dict_list(
            ('title', 'key'),
            constants.IMPACT_INDICATOR_REPORT)
        return (indicator_mapping, aggregated_indicators)

    def get_performance_indicators(self, projects):
        aggregated_indicators = (
            Report.get_aggregated_project_indicators(projects, False))
        mapping = tuple_to_dict_list(
            ('title', 'group'),
            constants.PERFORMANCE_INDICATOR_REPORTS[
                self.DEFAULT_PROJECT_TYPE])
        indicator_mapping = [(indicator['title'], indicator['group'][1])
                             for indicator in mapping]
        return (indicator_mapping, aggregated_indicators)
