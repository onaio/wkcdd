from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.community import Community
from wkcdd.models.project import Project
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
        community = self.request.context
        projects = community.projects
        constituency = Project.get_constituency(community)
        sub_county = Project.get_county(constituency)
        county = Project.get_county(sub_county)
        locations = {'constituency': constituency,
                     'sub_county': sub_county,
                     'county': county}

        return{
            'community': community,
            'projects': projects,
            'locations': locations,
            'impact_indicator_mapping': tuple_to_dict_list(
                ('title', 'key'),
                constants.IMPACT_INDICATOR_REPORT)
        }
