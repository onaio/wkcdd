from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.community import Community
from wkcdd.models.report import Report
from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.views.helpers import (
    build_dataset,
    generate_performance_indicators_for
)


@view_defaults(route_name='community')
class CommunityView(object):

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
        dataset = build_dataset("Project",
                                None,
                                impact_indicators,
                                projects
                                )
        search_criteria = {'view_by': 'projects'}
        return{
            'title': community.pretty,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'community': community,
            'search_criteria': search_criteria
        }

    @view_config(name='performance',
                 context=Community,
                 renderer='community_projects_performance_table.jinja2',
                 request_method='GET')
    def performance(self):
        community = self.request.context
        location_map = {
            'community': community.id,
            'constituency': '',
            'sub_county': '',
            'county': ''
        }
        indicators = generate_performance_indicators_for(
            location_map)
        project_types = indicators['project_types']
        aggregate_type = indicators['aggregate_type']
        sector_aggregated_indicators = (
            indicators['sector_aggregated_indicators'])
        return {
            'title': community.pretty,
            'aggregate_type': aggregate_type,
            'community': community,
            'project_types': project_types,
            'sector_aggregated_indicators': sector_aggregated_indicators,
        }

    def get_impact_indicators(self, projects):
        aggregated_indicators = (
            Report.get_impact_indicator_aggregation_for(projects))
        indicator_mapping = tuple_to_dict_list(
            ('title', 'key'),
            constants.IMPACT_INDICATOR_REPORT)
        return indicator_mapping, aggregated_indicators
