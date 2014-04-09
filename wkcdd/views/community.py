from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.community import Community
from wkcdd.models.project import Project
from wkcdd.models.report import Report
from wkcdd.models.location import Location
from wkcdd.views.helpers import build_dataset
from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models import helpers


@view_defaults(route_name='community')
class CommunityView(object):
    DEFAULT_PROJECT_TYPE = constants.DAIRY_GOAT_PROJECT_REPORT

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=Community,
                 renderer='community_projects_list.jinja2',
                 request_method='GET')
    def show(self):
        # TODO: eager load the constituency, county and sub-county
        # http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#eager-loading
        # http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#self-referential-query-strategies # noqa
        community = self.request.context
        projects = community.projects
        impact_indicators = Report.get_aggregated_impact_indicators(projects)
        dataset = build_dataset(Location.COMMUNITY,
                                None,
                                impact_indicators,
                                projects
                                )

        return{
            'title': community.name,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'community': community
        }

    @view_config(name='performance',
                 context=Community,
                 renderer='community_projects_performance_table.jinja2',
                 request_method='GET')
    def performance(self):
        community = self.request.context
        selected_project_type = (
            self.request.GET.get('type') or self.DEFAULT_PROJECT_TYPE)
        project_report_sectors = constants.PROJECT_REPORT_SECTORS
        if selected_project_type not in project_report_sectors.keys():
            selected_project_type = self.DEFAULT_PROJECT_TYPE
        projects = helpers.get_project_list(
            [community.id],
            Project.sector == project_report_sectors[selected_project_type])
        locations = self.get_locations(community)
        indicator_mapping, aggregated_indicators = (
            self.get_performance_indicators(
                projects,
                selected_project_type))
        selected_project_name = project_report_sectors[selected_project_type]
        return {
            'community': community,
            'locations': locations,
            'selected_project_type': selected_project_name,
            'project_report_sectors': project_report_sectors.items(),
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
            Report.get_impact_indicator_aggregation_for(projects))
        indicator_mapping = tuple_to_dict_list(
            ('title', 'key'),
            constants.IMPACT_INDICATOR_REPORT)
        return indicator_mapping, aggregated_indicators

    def get_performance_indicators(self, projects,
                                   project_type=DEFAULT_PROJECT_TYPE):
        aggregated_indicators = (
            Report.get_aggregated_performance_indicators(
                projects,
                project_type
            ))
        indicator_mapping = tuple_to_dict_list(
            ('title', 'group'),
            constants.PERFORMANCE_INDICATOR_REPORTS[
                project_type])
        return (indicator_mapping, aggregated_indicators)