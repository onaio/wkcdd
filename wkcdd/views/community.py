from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.community import Community
from wkcdd.models.project import Project
from wkcdd.models.report import Report
from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list


@view_defaults(route_name='community')
class CommunityView(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=Community,
                 renderer='community_projects_list.jinja2',
                 request_method='GET')
    def list_all_projects(self):
        # TODO: eager load the constituency, county and sub-county
        # http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#eager-loading
        # http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#self-referential-query-strategies # noqa
        community = self.request.context
        projects = community.projects
        constituency = Project.get_constituency(community)
        sub_county = Project.get_county(constituency)
        county = Project.get_county(sub_county)
        locations = {'constituency': constituency,
                     'sub_county': sub_county,
                     'county': county}
        aggregated_impact_indicators = (
            Report.get_aggregated_project_indicators(projects))
        return{
            'community': community,
            'locations': locations,
            'aggregated_impact_indicators': aggregated_impact_indicators,
            'impact_indicator_mapping': tuple_to_dict_list(
                ('title', 'key'),
                constants.IMPACT_INDICATOR_REPORT)
        }
