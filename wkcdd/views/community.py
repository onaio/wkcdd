from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.community import Community
from wkcdd.models.project import Project
from wkcdd.models.report import Report
from wkcdd.models.location import Location
from wkcdd.views.helpers import build_dataset


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
        impact_indicators = (
            Report.get_aggregated_project_indicators(projects))
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
            'locations': locations
        }
